# -*- coding: utf-8 -*-
"""
postgresと見積もりデータをやり取りする
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

# ------------------------------------------------------------------------------
# 設定・ロガーの初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 見積もり取得処理
# ------------------------------------------------------------------------------
async def get_quotes_by_user_id(user_id: str) -> List[PensionQuoteResponseModel]:
    """
    指定ユーザーの見積もり情報を RDS (PostgreSQL) から取得

    Parameters:
        user_id (str): ユーザーID

    Returns:
        List[PensionQuoteResponseModel]: 見積もり情報一覧
    """
    logger.info("見積もり取得処理開始: user_id=%s", user_id)

    dsn = config.postgres["dsn"]
    conn = None

    try:
        conn = await asyncpg.connect(dsn=dsn)

        rows = await conn.fetch("""
            SELECT
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
                scenario_data,
                created_at
            FROM quotes
            WHERE user_id = $1
            ORDER BY created_at DESC
        """, user_id)

        result = []
        for row in rows:
            scenarios_raw = json.loads(row["scenario_data"])

            scenarios = [
                PensionQuoteScenarioModel(
                    scenario_name=s["scenario_name"],
                    assumed_interest_rate=s["assumed_interest_rate"],
                    total_refund_amount=s["total_refund_amount"],
                    annual_annuity=s["annual_annuity"],
                    lump_sum_amount=s["lump_sum_amount"],
                    refund_on_15_years=s["refund_on_15_years"],
                    refund_rate_on_15_years=s["refund_rate_on_15_years"]
                )
                for s in scenarios_raw
            ]

            model = PensionQuoteResponseModel(
                quote_id=str(row["quote_id"]),
                user_id=str(row["user_id"]),
                contract_date=row["contract_date"],
                contract_interest_rate=row["contract_interest_rate"],
                total_paid_amount=row["total_paid_amount"],
                payment_period_years=row["payment_period_years"],
                pension_start_age=row["pension_start_age"],
                annual_tax_deduction=row["annual_tax_deduction"],
                scenarios=scenarios
            )
            result.append(model)

        logger.info("見積もり取得成功: %d件", len(result))
        return result

    except Exception as e:
        logger.exception("見積もり取得中にエラーが発生しました")
        raise

    finally:
        if conn:
            await conn.close()

# ------------------------------------------------------------------------------
# 見積もり単体取得処理
# ------------------------------------------------------------------------------
async def get_quote_by_id(quote_id: str) -> PensionQuoteResponseModel:
    """
    指定された見積もりIDから1件取得する

    Parameters:
        quote_id (str): 見積もりID

    Returns:
        PensionQuoteResponseModel: 見積もり詳細データ
    """
    logger.info("見積もり単体取得開始: quote_id=%s", quote_id)

    dsn = config.postgres["dsn"]
    conn = None

    try:
        conn = await asyncpg.connect(dsn=dsn)

        row = await conn.fetchrow("""
            SELECT
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
                scenario_data,
                created_at
            FROM quotes
            WHERE quote_id = $1
        """, quote_id)

        if not row:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="見積もりが存在しません")

        scenarios_raw = json.loads(row["scenario_data"])
        scenarios = [
            PensionQuoteScenarioModel(
                scenario_name=s["scenario_name"],
                assumed_interest_rate=s["assumed_interest_rate"],
                total_refund_amount=s["total_refund_amount"],
                annual_annuity=s["annual_annuity"],
                lump_sum_amount=s["lump_sum_amount"],
                refund_on_15_years=s["refund_on_15_years"],
                refund_rate_on_15_years=s["refund_rate_on_15_years"]
            )
            for s in scenarios_raw
        ]

        return PensionQuoteResponseModel(
                    user_id=str(row["user_id"]),
                    quote_id=str(row["quote_id"]),
                    contract_date=row["contract_date"],
                    contract_interest_rate=row["contract_interest_rate"],
                    total_paid_amount=row["total_paid_amount"],
                    payment_period_years=row["payment_period_years"],
                    pension_start_age=row["pension_start_age"],
                    annual_tax_deduction=row["annual_tax_deduction"],
                    scenarios=scenarios
                )

    except Exception as e:
        logger.exception("見積もり単体取得中にエラーが発生しました")
        raise

    finally:
        if conn:
            await conn.close()

# ------------------------------------------------------------------------------
# 見積もりステータス更新処理
# ------------------------------------------------------------------------------
async def update_quote_state(quote_id: str, user_id: str, new_state: str) -> PensionQuoteResponseModel:
    """
    指定された見積もりIDの状態を更新する（例：applied）

    Parameters:
        quote_id (str): 見積もりID
        user_id (str): ログインユーザーID（認可チェック用）
        new_state (str): 更新後の状態（例："applied"）

    Returns:
        PensionQuoteResponseModel: 更新後の見積もり情報
    """
    logger.info("見積もり状態更新開始: quote_id=%s, new_state=%s", quote_id, new_state)

    dsn = config.postgres["dsn"]
    conn = None

    try:
        conn = await asyncpg.connect(dsn=dsn)

        row = await conn.fetchrow("SELECT user_id FROM quotes WHERE quote_id = $1", quote_id)
        if not row:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="見積もりが存在しません")

        if row["user_id"] != user_id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他人の見積もりは更新できません")

        await conn.execute("""
            UPDATE quotes
            SET quote_state = $1
            WHERE quote_id = $2
        """, new_state, quote_id)

        logger.info("状態更新完了: quote_id=%s", quote_id)

        # 更新後の見積もりを返す
        return await get_quote_by_id(quote_id)

    except Exception as e:
        logger.exception("見積もり状態更新中にエラーが発生しました")
        raise

    finally:
        if conn:
            await conn.close()

# ------------------------------------------------------------------------------
# 見積もり保存処理
# ------------------------------------------------------------------------------
async def save_quote(
    user_id: str,
    request: PensionQuoteRequestModel,
    response: PensionQuoteResponseModel
):
    """
    見積もりデータを PostgreSQL quotes テーブルに保存する

    Parameters:
        user_id (str): 見積もりを実行したユーザーID
        request (PensionQuoteRequestModel): 見積もり入力データ
        response (PensionQuoteResponseModel): 見積もり結果データ
    """
    logger.info("見積もり保存処理開始: user_id=%s, quote_id=%s", user_id, response.quote_id)

    try:
        # PostgreSQLへ接続
        dsn = config.postgres["dsn"]
        conn = await asyncpg.connect(dsn=dsn)

       # INSERT実行
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
            request.birth_date,
            request.gender,
            request.monthly_premium,
            request.payment_period_years,
            request.tax_deduction_enabled,
            response.contract_date,
            response.contract_interest_rate,
            response.total_paid_amount,
            response.pension_start_age,
            response.annual_tax_deduction,
            json.dumps([s.dict() for s in response.scenarios])
        )

        logger.info("見積もり保存成功: quote_id=%s", response.quote_id)

    except Exception as e:
        # エラー発生時はログ出力し、例外を再送出
        logger.exception("見積もり保存失敗: quote_id=%s", response.quote_id)
        raise

    finally:
        # 接続クローズは必ず実行
        await conn.close()