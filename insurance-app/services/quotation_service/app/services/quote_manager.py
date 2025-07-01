# -*- coding: utf-8 -*-
"""
quotesテーブルとのデータやり取りを担うモジュール
- 見積もりの取得
- 見積もりの保存
- ステータス更新（申込時）
"""

import logging
import json
import asyncpg
from typing import List

from app.config.config import Config
from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    PensionQuoteScenarioModel
)

from fastapi import HTTPException, status

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# 見積もり一覧取得（ユーザー単位）
# ------------------------------------------------------------------------------
async def get_quotes_by_user_id(user_id: str) -> List[PensionQuoteResponseModel]:
    """
    指定ユーザーの見積もりを取得する（最新順）

    Parameters:
        user_id (str): ユーザーID

    Returns:
        List[PensionQuoteResponseModel]: レスポンス用モデルのリスト
    """
    logger.info("見積もり取得開始: user_id=%s", user_id)
    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        logger.debug("PostgreSQL接続成功")

        rows = await conn.fetch("""
            SELECT * FROM quotes
            WHERE user_id = $1
            ORDER BY created_at DESC
        """, user_id)
        logger.debug("クエリ実行成功: 件数=%d", len(rows))

        result = []
        for row in rows:
            scenarios = json.loads(row["scenario_data"])
            response = PensionQuoteResponseModel(
                quote_id=str(row["quote_id"]),
                user_id=str(row["user_id"]),
                contract_date=row["contract_date"],
                contract_interest_rate=row["contract_interest_rate"],
                total_paid_amount=row["total_paid_amount"],
                payment_period_years=row["payment_period_years"],
                pension_start_age=row["pension_start_age"],
                annual_tax_deduction=row["annual_tax_deduction"],
                scenarios=[PensionQuoteScenarioModel(**s) for s in scenarios]
            )
            result.append(response)

        logger.info("見積もり取得成功: %d件", len(result))
        return result

    except Exception:
        logger.exception("見積もり取得中にエラー")
        raise

    finally:
        if conn:
            await conn.close()
            logger.debug("PostgreSQL接続クローズ")


# ------------------------------------------------------------------------------
# 見積もり単体取得（ID指定）
# ------------------------------------------------------------------------------
async def get_quote_by_id(quote_id: str) -> PensionQuoteResponseModel:
    """
    指定IDの見積もりを1件取得

    Parameters:
        quote_id (str): 見積もりID

    Returns:
        PensionQuoteResponseModel: 表示用のレスポンスモデル
    """
    logger.info("見積もり単体取得: quote_id=%s", quote_id)
    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        logger.debug("PostgreSQL接続成功")

        row = await conn.fetchrow("SELECT * FROM quotes WHERE quote_id = $1", quote_id)
        if not row:
            logger.warning("見積もりが存在しません: quote_id=%s", quote_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="見積もりが存在しません")

        scenarios = json.loads(row["scenario_data"])
        logger.debug("見積もりデータ取得成功")

        return PensionQuoteResponseModel(
            quote_id=str(row["quote_id"]),
            user_id=str(row["user_id"]),
            contract_date=row["contract_date"],
            contract_interest_rate=row["contract_interest_rate"],
            total_paid_amount=row["total_paid_amount"],
            payment_period_years=row["payment_period_years"],
            pension_start_age=row["pension_start_age"],
            annual_tax_deduction=row["annual_tax_deduction"],
            scenarios=[PensionQuoteScenarioModel(**s) for s in scenarios]
        )

    except Exception:
        logger.exception("見積もり単体取得中にエラー")
        raise

    finally:
        if conn:
            await conn.close()
            logger.debug("PostgreSQL接続クローズ")


# ------------------------------------------------------------------------------
# 見積もり保存処理（新規登録）
# ------------------------------------------------------------------------------
async def save_quote(user_id: str, request: PensionQuoteRequestModel, response: PensionQuoteResponseModel):
    """
    見積もりをquotesテーブルに保存する

    Parameters:
        user_id (str): ユーザーID
        request (PensionQuoteRequestModel): 入力内容
        response (PensionQuoteResponseModel): 計算結果（保存対象）
    """
    logger.info("見積もり保存: quote_id=%s", response.quote_id)
    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        logger.debug("PostgreSQL接続成功")

        logger.debug("INSERT前のデータ: %s", json.dumps(response.dict()))

        await conn.execute("""
            INSERT INTO quotes (
                quote_id,
                user_id,
                birth_date,
                gender,
                monthly_premium,
                payment_period_years,
                tax_deduction_enabled,
                contract_date,
                contract_interest_rate,
                total_paid_amount,
                pension_start_age,
                annual_tax_deduction,
                scenario_data
            )
            VALUES (
                $1, $2, $3, $4, $5, $6, $7,
                $8, $9, $10, $11, $12, $13
            )
        """,
            response.quote_id,
            user_id,
            request.birth_date.date(),
            "male" if request.gender == "男" else "female",
            request.monthly_premium,
            request.payment_period_years,
            request.tax_deduction_enabled,
            response.contract_date.date(),
            response.contract_interest_rate,
            response.total_paid_amount,
            response.pension_start_age,
            response.annual_tax_deduction,
            json.dumps([s.dict() for s in response.scenarios])
        )

        logger.info("見積もり保存完了")

    except Exception:
        logger.exception("見積もり保存失敗: quote_id=%s", response.quote_id)
        raise

    finally:
        if conn:
            await conn.close()
            logger.debug("PostgreSQL接続クローズ")


# ------------------------------------------------------------------------------
# ステータス更新処理（任意ステータスに対応）
# ------------------------------------------------------------------------------
async def mark_quote_state(quote_id: str, user_id: str, new_state: str) -> PensionQuoteResponseModel:
    """
    指定された見積もりのステータスを更新する（任意の quote_state に対応）

    Parameters:
        quote_id (str): 見積もりID
        user_id (str): 呼び出し元のユーザー（認可チェック用）
        new_state (str): 新しいステータス（例："applied", "canceled" など）

    Returns:
        PensionQuoteResponseModel: 更新後の見積もり
    """
    logger.info("ステータス更新開始: quote_id=%s, new_state=%s", quote_id, new_state)
    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        logger.debug("PostgreSQL接続成功")

        row = await conn.fetchrow("SELECT user_id FROM quotes WHERE quote_id = $1", quote_id)
        if not row:
            logger.warning("見積もり未存在: quote_id=%s", quote_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="見積もりが存在しません")

        if str(row["user_id"]) != user_id:
            logger.debug(f"quote_user_id: {row['user_id']}")
            logger.debug(f"user_id: {user_id}")
            logger.warning("認可エラー: 他人の見積もりに対する操作をブロック")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他人の見積もりは更新できません")

        await conn.execute("""
            UPDATE quotes
            SET quote_state = $2
            WHERE quote_id = $1
        """, quote_id, new_state)

        logger.info("ステータス更新完了: quote_id=%s → %s", quote_id, new_state)
        return await get_quote_by_id(quote_id)

    except Exception:
        logger.exception("ステータス更新中にエラー")
        raise

    finally:
        if conn:
            await conn.close()
            logger.debug("PostgreSQL接続クローズ")


# ------------------------------------------------------------------------------
# 任意フィールドの更新処理（ステータス以外の用途にも対応）
# ------------------------------------------------------------------------------
async def update_quote(quote_id: str, user_id: str, updates: dict) -> PensionQuoteResponseModel:
    """
    指定された見積もりレコードの任意のフィールドを更新する（ステータス以外）

    Parameters:
        quote_id (str): 見積もりID
        user_id (str): 呼び出し元ユーザー（認可チェック用）
        updates (dict): 更新対象のフィールド名と値の辞書

    Returns:
        PensionQuoteResponseModel: 更新後の見積もり
    """
    logger.info("見積もり更新処理開始: quote_id=%s, updates=%s", quote_id, updates)

    allowed_fields = {
        "monthly_premium", "payment_period_years", "tax_deduction_enabled",
        "contract_date", "contract_interest_rate", "total_paid_amount",
        "pension_start_age", "annual_tax_deduction", "scenario_data"
    }

    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    logger.debug("更新対象フィールド: %s", filtered_updates)

    if not filtered_updates:
        logger.warning("更新対象なし: 許可されたフィールドが含まれていません")
        raise HTTPException(status_code=400, detail="更新可能な項目が含まれていません")

    set_clause = ", ".join([f"{field} = ${i+2}" for i, field in enumerate(filtered_updates)])
    values = list(filtered_updates.values())

    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        logger.debug("PostgreSQL接続成功")

        row = await conn.fetchrow("SELECT user_id FROM quotes WHERE quote_id = $1", quote_id)
        if not row:
            logger.warning("見積もり未存在: quote_id=%s", quote_id)
            raise HTTPException(status_code=404, detail="見積もりが存在しません")
        if row["user_id"] != user_id:
            logger.warning("認可エラー: 他人の見積もり")
            raise HTTPException(status_code=403, detail="他人の見積もりは更新できません")

        query = f"UPDATE quotes SET {set_clause} WHERE quote_id = $1"
        logger.debug("生成されたクエリ: %s", query)
        await conn.execute(query, quote_id, *values)

        logger.info("見積もり更新完了: quote_id=%s", quote_id)
        return await get_quote_by_id(quote_id)

    except Exception:
        logger.exception("見積もり更新中にエラー")
        raise

    finally:
        if conn:
            await conn.close()
            logger.debug("PostgreSQL接続クローズ")
