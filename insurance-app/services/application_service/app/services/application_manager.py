# -*- coding: utf-8 -*-
"""
保険申込処理ロジック

- quotation_service から見積もりを取得・検証・状態変更
- PostgreSQL に申込レコードを保存／取得／ステータス更新
- NATS に申込完了/キャンセルイベントを発行
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import uuid
import json
import httpx
import asyncpg
from datetime import datetime
from typing import Dict
from typing import List

from app.config.config import Config
from app.models.applications import (
    ApplicationResponseModel,
    PensionQuoteScenarioModel,
    ApplicationStatusResponseModel
)
from app.models.events import (
    ApplicationConfirmedEvent,
    ApplicationCancelledEvent
)
from app.services.nats_publisher import publish_event

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

# ------------------------------------------------------------------------------
# 保険申込の新規作成処理
# ------------------------------------------------------------------------------
async def create_application(user_id: str, quote: Dict, access_token: str, status: str = "applied") -> ApplicationResponseModel:
    """
    指定見積もりをもとに申込処理を行い、DB登録および NATS イベント発行を行う
    """
    quote_id = quote.get("quote_id")
    if quote.get("user_id") != user_id:
        raise ValueError("他人の見積もりに対して申込処理はできません")
    if quote.get("contract_date") is None:
        raise ValueError("見積もりに契約日が設定されていません")

    # birth_date と contract_date を datetime.date に変換（必要に応じて）
    birth_date = quote["birth_date"]
    if isinstance(birth_date, str):
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()

    contract_date = quote["contract_date"]
    if isinstance(contract_date, str):
        contract_date = datetime.strptime(contract_date, "%Y-%m-%d").date()

    # scenario_data を JSON 文字列に変換（JSONB対応）
    scenario_json = json.dumps(quote["scenarios"], ensure_ascii=False)

    # DBに申し込み情報を格納する
    application_id = str(uuid.uuid4())
    now = datetime.utcnow()
    dsn = config.postgres["dsn"]
    conn = await asyncpg.connect(dsn=dsn)
    try:
        await conn.execute("""
            INSERT INTO applications (
                application_id, quote_id, user_id, application_status,
                user_consent, applied_at,
                snapshot_birth_date, snapshot_gender,
                snapshot_monthly_premium, snapshot_payment_period_years, snapshot_tax_deduction_enabled,
                snapshot_contract_date, snapshot_contract_interest_rate,
                snapshot_total_paid_amount, snapshot_pension_start_age, snapshot_annual_tax_deduction,
                scenario_data
            )
            VALUES (
                $1, $2, $3, $4,
                $5, $6,
                $7, $8, $9, $10, $11,
                $12, $13, $14, $15, $16,
                $17
            )
        """, application_id, quote_id, user_id, status,
             True, now,
             birth_date, quote["gender"],
             quote["monthly_premium"], quote["payment_period_years"], quote["tax_deduction_enabled"],
             contract_date, quote["contract_interest_rate"],
             quote["total_paid_amount"], quote["pension_start_age"], quote["annual_tax_deduction"],
             scenario_json)
    finally:
        await conn.close()

    # NATS に ApplicationConfirmed イベントを発行
    event = ApplicationConfirmedEvent(
        event="ApplicationConfirmed",
        quote_id=quote_id,
        user_id=user_id,
        application_id=application_id,
        confirmed_at=now.isoformat()
    )
    await publish_event("applications.ApplicationConfirmed", event.dict())

    return ApplicationResponseModel(
        application_id=application_id,
        quote_id=quote_id,
        status=status,
        snapshot_birth_date=birth_date,
        snapshot_gender=quote["gender"],
        snapshot_monthly_premium=quote["monthly_premium"],
        snapshot_payment_period_years=quote["payment_period_years"],
        snapshot_tax_deduction_enabled=quote["tax_deduction_enabled"],
        snapshot_contract_date=contract_date,
        snapshot_contract_interest_rate=quote["contract_interest_rate"],
        snapshot_total_paid_amount=quote["total_paid_amount"],
        snapshot_pension_start_age=quote["pension_start_age"],
        snapshot_annual_tax_deduction=quote["annual_tax_deduction"],
        scenario_data=[PensionQuoteScenarioModel(**s) for s in quote["scenarios"]]
    )

# ------------------------------------------------------------------------------
# 保険申込ステータスを更新（キャンセル・差戻し等）
# ------------------------------------------------------------------------------
async def update_application_status(application_id: str, user_id: str, new_status: str) -> ApplicationStatusResponseModel:
    """
    指定された申込のステータスを更新し、必要に応じて NATS イベントも発行する
    """
    logger.info("申込ステータス更新: application_id=%s, user_id=%s, new_status=%s", application_id, user_id, new_status)
    dsn = config.postgres["dsn"]
    conn = await asyncpg.connect(dsn=dsn)

    try:
        row = await conn.fetchrow("""
            SELECT application_id, quote_id, user_id
            FROM applications
            WHERE application_id = $1 AND deleted_at IS NULL
        """, application_id)

        if not row:
            raise ValueError("申込が見つかりません")
        if str(row["user_id"]) != user_id:
            raise ValueError("他人の申込にアクセスできません")

        await conn.execute("""
            UPDATE applications
            SET application_status = $1
            WHERE application_id = $2
        """, new_status, application_id)

        # Step 2: NATS に ApplicationCancelled イベントを発行（必要時のみ）
        if new_status == "cancelled":
            event = ApplicationCancelledEvent(
                event="ApplicationCancelled",
                quote_id=str(row["quote_id"]),
                user_id=user_id,
                application_id=application_id,
                cancelled_at=datetime.utcnow().isoformat()
            )
            await publish_event("applications.ApplicationCancelled", event.dict())

        return ApplicationStatusResponseModel(
            application_id=str(row["application_id"]),
            quote_id=str(row["quote_id"]),
            status=new_status
        )

    finally:
        await conn.close()

# ------------------------------------------------------------------------------
# 自ユーザーの申込一覧を取得
# ------------------------------------------------------------------------------
async def get_applications_by_user_id(user_id: str) -> List[ApplicationResponseModel]:
    """
    指定ユーザーIDに紐づくすべての申込一覧を取得する

    Parameters:
        user_id (str): ユーザーID（Keycloakのsub）

    Returns:
        List[ApplicationResponseModel]: 申込情報のリスト（スナップショット含む）
    """
    logger.info("申込一覧取得: user_id=%s", user_id)
    dsn = config.postgres["dsn"]
    conn = await asyncpg.connect(dsn=dsn)

    try:
        rows = await conn.fetch("""
            SELECT
                application_id, quote_id, application_status,
                snapshot_birth_date, snapshot_gender,
                snapshot_monthly_premium, snapshot_payment_period_years, snapshot_tax_deduction_enabled,
                snapshot_contract_date, snapshot_contract_interest_rate,
                snapshot_total_paid_amount, snapshot_pension_start_age, snapshot_annual_tax_deduction,
                scenario_data
            FROM applications
            WHERE user_id = $1 AND deleted_at IS NULL
            ORDER BY applied_at DESC
        """, user_id)

        return [
            ApplicationResponseModel(
                application_id=str(row["application_id"]),
                quote_id=str(row["quote_id"]),
                status=row["application_status"],
                snapshot_birth_date=row["snapshot_birth_date"],
                snapshot_gender=row["snapshot_gender"],
                snapshot_monthly_premium=row["snapshot_monthly_premium"],
                snapshot_payment_period_years=row["snapshot_payment_period_years"],
                snapshot_tax_deduction_enabled=row["snapshot_tax_deduction_enabled"],
                snapshot_contract_date=row["snapshot_contract_date"],
                snapshot_contract_interest_rate=float(row["snapshot_contract_interest_rate"]),
                snapshot_total_paid_amount=row["snapshot_total_paid_amount"],
                snapshot_pension_start_age=row["snapshot_pension_start_age"],
                snapshot_annual_tax_deduction=row["snapshot_annual_tax_deduction"],
                scenario_data=[
                    PensionQuoteScenarioModel(**s) for s in json.loads(row["scenario_data"])
                ]
            )
            for row in rows
        ]

    finally:
        await conn.close()

# ------------------------------------------------------------------------------
# 自ユーザーの特定申込を取得
# ------------------------------------------------------------------------------
async def get_application_by_id(application_id: str, user_id: str) -> ApplicationResponseModel:
    """
    指定された申込IDの詳細情報を取得する（本人の申込のみ）

    Parameters:
        application_id (str): 対象申込ID
        user_id (str): ユーザーID（本人確認用）

    Returns:
        ApplicationResponseModel: 詳細な申込情報（スナップショット付き）

    Raises:
        ValueError: 他人の申込、または見つからない場合
    """
    logger.info("申込詳細取得: application_id=%s, user_id=%s", application_id, user_id)
    dsn = config.postgres["dsn"]
    conn = await asyncpg.connect(dsn=dsn)

    try:
        row = await conn.fetchrow("""
            SELECT
                application_id, quote_id, user_id, application_status,
                snapshot_birth_date, snapshot_gender,
                snapshot_monthly_premium, snapshot_payment_period_years, snapshot_tax_deduction_enabled,
                snapshot_contract_date, snapshot_contract_interest_rate,
                snapshot_total_paid_amount, snapshot_pension_start_age, snapshot_annual_tax_deduction,
                scenario_data
            FROM applications
            WHERE application_id = $1 AND deleted_at IS NULL
        """, application_id)

        if not row:
            raise ValueError("申込が見つかりません")

        if str(row["user_id"]) != user_id:
            raise ValueError("他人の申込にアクセスできません")

        return ApplicationResponseModel(
                application_id=str(row["application_id"]),
                quote_id=str(row["quote_id"]),
                status=row["application_status"],
                snapshot_birth_date=row["snapshot_birth_date"],
                snapshot_gender=row["snapshot_gender"],
                snapshot_monthly_premium=row["snapshot_monthly_premium"],
                snapshot_payment_period_years=row["snapshot_payment_period_years"],
                snapshot_tax_deduction_enabled=row["snapshot_tax_deduction_enabled"],
                snapshot_contract_date=row["snapshot_contract_date"],
                snapshot_contract_interest_rate=float(row["snapshot_contract_interest_rate"]),
                snapshot_total_paid_amount=row["snapshot_total_paid_amount"],
                snapshot_pension_start_age=row["snapshot_pension_start_age"],
                snapshot_annual_tax_deduction=row["snapshot_annual_tax_deduction"],
                scenario_data=[
                    PensionQuoteScenarioModel(**s) for s in json.loads(row["scenario_data"])
                ]
        )

    finally:
        await conn.close()
