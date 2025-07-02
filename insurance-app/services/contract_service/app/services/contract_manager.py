# -*- coding: utf-8 -*-
"""
contractsテーブルとのデータやり取りを担うモジュール
- 契約の取得（一覧・単体）
- 契約の作成（申込に基づく）
- 契約のキャンセル（ステータス更新）
"""

import logging
import json
import asyncpg
from typing import List

from app.config.config import Config
from app.models.contracts import (
    ContractResponseModel,
    ContractScenarioModel
)
from app.services.application_manager import get_application_by_id
from app.services.quote_manager import get_quote_by_id
from fastapi import HTTPException, status
from uuid import uuid4
from datetime import datetime

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 契約一覧取得（ユーザー単位）
# ------------------------------------------------------------------------------
async def get_contracts_by_user_id(user_id: str) -> List[ContractResponseModel]:
    """
    指定ユーザーの契約一覧を取得する（最新順）

    Parameters:
        user_id (str): ユーザーID

    Returns:
        List[ContractResponseModel]: レスポンスモデルのリスト
    """
    logger.info("契約一覧取得開始: user_id=%s", user_id)
    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        logger.debug("PostgreSQL接続成功")

        rows = await conn.fetch("""
            SELECT * FROM contracts
            WHERE user_id = $1
            ORDER BY created_at DESC
        """, user_id)
        logger.debug("クエリ実行成功: 件数=%d", len(rows))

        result = []
        for row in rows:
            scenarios = json.loads(row["scenario_data"])
            contract = ContractResponseModel(
                contract_id=str(row["contract_id"]),
                user_id=str(row["user_id"]),
                application_id=str(row["application_id"]),
                quote_id=str(row["quote_id"]),
                contract_status=row.get("contract_status", "active"),
                user_consent=row["user_consent"],
                applied_at=row["applied_at"],
                birth_date=row["birth_date"],
                gender="男" if row["gender"] == "male" else "女",
                monthly_premium=row["monthly_premium"],
                payment_period_years=row["payment_period_years"],
                tax_deduction_enabled=row["tax_deduction_enabled"],
                contract_date=row["contract_date"],
                contract_interest_rate=row["contract_interest_rate"],
                total_paid_amount=row["total_paid_amount"],
                pension_start_age=row["pension_start_age"],
                annual_tax_deduction=row["annual_tax_deduction"],
                scenarios=[ContractScenarioModel(**s) for s in scenarios],
                created_at=row["created_at"],
                cancelled_at=row.get("cancelled_at")
            )
            result.append(contract)

        logger.info("契約一覧取得成功: %d件", len(result))
        return result

    except Exception:
        logger.exception("契約一覧取得中にエラー")
        raise

    finally:
        if conn:
            await conn.close()
            logger.debug("PostgreSQL接続クローズ")

# ------------------------------------------------------------------------------
# 契約単体取得（ID指定）
# ------------------------------------------------------------------------------
async def get_contract_by_id(contract_id: str) -> ContractResponseModel:
    """
    指定IDの契約を1件取得

    Parameters:
        contract_id (str): 契約ID

    Returns:
        ContractResponseModel: 表示用のレスポンスモデル
    """
    logger.info("契約単体取得: contract_id=%s", contract_id)
    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        row = await conn.fetchrow("SELECT * FROM contracts WHERE contract_id = $1", contract_id)
        if not row:
            logger.warning("契約が存在しません: contract_id=%s", contract_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="契約が存在しません")

        scenarios = json.loads(row["scenario_data"])
        return ContractResponseModel(
            contract_id=str(row["contract_id"]),
            user_id=str(row["user_id"]),
            application_id=str(row["application_id"]),
            quote_id=str(row["quote_id"]),
            contract_status=row.get("contract_status", "active"),
            user_consent=row["user_consent"],
            applied_at=row["applied_at"],
            birth_date=row["birth_date"],
            gender="男" if row["gender"] == "male" else "女",
            monthly_premium=row["monthly_premium"],
            payment_period_years=row["payment_period_years"],
            tax_deduction_enabled=row["tax_deduction_enabled"],
            contract_date=row["contract_date"],
            contract_interest_rate=row["contract_interest_rate"],
            total_paid_amount=row["total_paid_amount"],
            pension_start_age=row["pension_start_age"],
            annual_tax_deduction=row["annual_tax_deduction"],
            scenarios=[ContractScenarioModel(**s) for s in scenarios],
            created_at=row["created_at"],
            cancelled_at=row.get("cancelled_at")
        )

    except Exception:
        logger.exception("契約単体取得中にエラー")
        raise

    finally:
        if conn:
            await conn.close()

# ------------------------------------------------------------------------------
# 契約作成処理（申込IDをもとに生成）
# ------------------------------------------------------------------------------
async def create_contract_by_application_id(application_id: str, user_id: str) -> ContractResponseModel:
    """
    申込IDに基づいて契約を新規作成する

    Parameters:
        application_id (str): 対象の申込ID
        user_id (str): トークンのユーザーID

    Returns:
        ContractResponseModel: 作成された契約情報
    """
    logger.info("契約作成処理開始: application_id=%s", application_id)

    # 関連情報を取得
    application = await get_application_by_id(application_id)
    if str(application.user_id) != user_id:
        raise HTTPException(status_code=403, detail="他人の申込に対する契約は作成できません")

    quote = await get_quote_by_id(str(application.quote_id))

    contract_id = str(uuid4())
    applied_at = application.applied_at
    now = datetime.utcnow()

    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])
        logger.debug("PostgreSQL接続成功")

        await conn.execute("""
            INSERT INTO contracts (
                contract_id,
                quote_id,
                application_id,
                user_id,
                user_consent,
                applied_at,
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
                created_at,
                contract_status
            ) VALUES (
                $1, $2, $3, $4, $5, $6,
                $7, $8, $9, $10, $11,
                $12, $13, $14, $15, $16,
                $17, $18, 'active'
            )
        """,
            contract_id,
            str(quote.quote_id),
            str(application.application_id),
            user_id,
            application.user_consent,
            applied_at,
            application.snapshot_birth_date,
            "male" if application.snapshot_gender == "男" else "female",
            application.snapshot_monthly_premium,
            application.snapshot_payment_period_years,
            application.snapshot_tax_deduction_enabled,
            application.snapshot_contract_date,
            application.snapshot_contract_interest_rate,
            quote.total_paid_amount,
            quote.pension_start_age,
            quote.annual_tax_deduction,
            json.dumps([s.dict() for s in quote.scenarios]),
            now
        )

        logger.info("契約作成完了: contract_id=%s", contract_id)
        return await get_contract_by_id(contract_id)

    except Exception:
        logger.exception("契約作成中にエラー")
        raise

    finally:
        if conn:
            await conn.close()

# ------------------------------------------------------------------------------
# 契約キャンセル処理（ステータス変更）
# ------------------------------------------------------------------------------
async def cancel_contract(contract_id: str, user_id: str) -> ContractResponseModel:
    """
    指定された契約をキャンセル（解約）状態に更新する

    Parameters:
        contract_id (str): 対象の契約ID
        user_id (str): 操作を実行するユーザーID

    Returns:
        ContractResponseModel: 更新後の契約情報
    """
    logger.info("契約キャンセル処理開始: contract_id=%s", contract_id)
    conn = None
    try:
        conn = await asyncpg.connect(dsn=config.postgres["dsn"])

        row = await conn.fetchrow("SELECT user_id, contract_status FROM contracts WHERE contract_id = $1", contract_id)
        if not row:
            raise HTTPException(status_code=404, detail="契約が存在しません")

        if str(row["user_id"]) != user_id:
            raise HTTPException(status_code=403, detail="他人の契約はキャンセルできません")

        if row["contract_status"] == "cancelled":
            raise HTTPException(status_code=400, detail="契約はすでにキャンセルされています")

        await conn.execute("""
            UPDATE contracts
            SET contract_status = 'cancelled',
                cancelled_at = $2
            WHERE contract_id = $1
        """, contract_id, datetime.utcnow())

        logger.info("契約キャンセル完了: contract_id=%s", contract_id)
        return await get_contract_by_id(contract_id)

    except Exception:
        logger.exception("契約キャンセル中にエラー")
        raise

    finally:
        if conn:
            await conn.close()

# ------------------------------------------------------------------------------
# 契約更新処理（任意フィールドに対応）
# ------------------------------------------------------------------------------
async def update_contract(contract_id: str, user_id: str, updates: dict) -> ContractResponseModel:
    """
    指定された契約レコードの任意のフィールドを更新する

    Parameters:
        contract_id (str): 契約ID
        user_id (str): 呼び出し元ユーザー（認可チェック用）
        updates (dict): 更新対象のフィールド名と値の辞書

    Returns:
        ContractResponseModel: 更新後の契約情報
    """
    logger.info("契約更新処理開始: contract_id=%s, updates=%s", contract_id, updates)

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

        row = await conn.fetchrow("SELECT user_id FROM contracts WHERE contract_id = $1", contract_id)
        if not row:
            logger.warning("契約未存在: contract_id=%s", contract_id)
            raise HTTPException(status_code=404, detail="契約が存在しません")
        if str(row["user_id"]) != user_id:
            logger.warning("認可エラー: 他人の契約")
            raise HTTPException(status_code=403, detail="他人の契約は更新できません")

        query = f"UPDATE contracts SET {set_clause} WHERE contract_id = $1"
        logger.debug("生成されたクエリ: %s", query)
        await conn.execute(query, contract_id, *values)

        logger.info("契約更新完了: contract_id=%s", contract_id)
        return await get_contract_by_id(contract_id)

    except Exception:
        logger.exception("契約更新中にエラー")
        raise

    finally:
        if conn:
            await conn.close()
            logger.debug("PostgreSQL接続クローズ")
