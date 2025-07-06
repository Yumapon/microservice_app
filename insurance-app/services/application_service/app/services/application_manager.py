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
from uuid import UUID
import asyncpg
from datetime import datetime
from typing import Dict
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from motor.motor_asyncio import AsyncIOMotorClient

from fastapi import HTTPException

from app.config.config import Config
from app.db_models.applications import (
    Application,
    ApplicationDetail
)
from app.models.applications import (
    PensionApplicationScenarioModel,
    PensionApplicationResponseModel,
    PensionApplicationRequestModel,
    QuoteSummaryModel,
    QuoteScenarioModel,
    ApplicationBeneficiariesModel
)

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()
rules = config.pension

####参照処理

# ------------------------------------------------------------------------------
# 申し込み一覧取得（ユーザー単位、シナリオなし）
# ------------------------------------------------------------------------------
async def get_applications_by_user_id(
    session: AsyncSession,
    user_id: UUID
) -> List[PensionApplicationResponseModel]:
    """
    指定ユーザーの申込一覧を取得
    """
    logger.info("申込一覧取得: user_id=%s", user_id)

    stmt = (
        select(Application, ApplicationDetail)
        .join(ApplicationDetail, Application.application_id == ApplicationDetail.application_id)
        .where(Application.user_id == user_id)
        .order_by(Application.applied_at.desc())
    )
    results = await session.execute(stmt)

    return [
        _build_application_response_model(application, detail, scenarios=[], beneficiaries=[])
        for application, detail in results.all()
    ]

# ------------------------------------------------------------------------------
# 申し込み単体取得
# ------------------------------------------------------------------------------
async def get_application_by_application_id(
        session: AsyncSession, 
        application_id: UUID, 
        user_id: UUID
    ) -> PensionApplicationResponseModel:
    """
    申し込みIDを指定して1件取得
    """
    logger.info("申込取得: application_id=%s, user_id=%s", application_id, user_id)

    result = await session.execute(
        select(Application, ApplicationDetail)
        .join(ApplicationDetail, Application.application_id == ApplicationDetail.application_id)
        .where(Application.application_id == application_id)
    )
    record = result.first()
    if not record:
        raise HTTPException(status_code=404, detail="申し込みが存在しません")
    
    application, detail = record
    if str(application.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="他人の申し込みは更新できません")

    logger.info(f"application{application}")
    response = _build_application_response_model(application, detail, scenarios=[], beneficiaries=[])
    return response

# ------------------------------------------------------------------------------
# 申し込みシナリオ一覧取得（申し込みID単位）
# ------------------------------------------------------------------------------
async def get_scenarios_by_application_id(
    mongo_client: AsyncIOMotorClient,
    application_id: str
) -> List[PensionApplicationScenarioModel]:
    """
    指定された application_id に対応するシナリオ情報を MongoDB から取得する。
    """
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["scenario_collection"]
        logger.info(f"MongoDBシナリオ取得開始 (application_id={application_id})")

        cursor = mongo_client[db_name][collection_name].find({"application_id": application_id})
        documents = await cursor.to_list(length=None)

        logger.info(f"MongoDBシナリオ取得成功 (application_id={application_id}, 件数={len(documents)})")

        scenarios = [PensionApplicationScenarioModel(**doc) for doc in documents]
        return scenarios

    except Exception as e:
        logger.error(f"MongoDBシナリオ取得失敗 (application_id={application_id}): {e}")
        return []
    
# ------------------------------------------------------------------------------
# 申し込み保険金受け取り代理人取得（申し込みID単位）
# ------------------------------------------------------------------------------
async def get_beneficiaries_by_application_id(
    mongo_client: AsyncIOMotorClient,
    application_id: str
) -> List[ApplicationBeneficiariesModel]:
    """
    指定された application_id に対応する保険金受け取り代理人情報を MongoDB から取得する。
    """
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["collection"]
        collection = mongo_client[db_name][collection_name]
        logger.info(f"MongoDB保険金受け取り代理人情報取得開始 (application_id={application_id})")

        cursor = collection.find({"application_id": application_id})
        documents = await cursor.to_list(length=None)

        logger.info(f"MongoDB保険金受け取り代理人情報取得成功 (application_id={application_id}, 件数={len(documents)})")

        beneficiaries = [ApplicationBeneficiariesModel(**doc) for doc in documents]
        return beneficiaries

    except Exception as e:
        logger.error(f"MongoDB保険金受け取り代理人情報取得失敗 (application_id={application_id}): {e}")
        return []

####更新処理

# ------------------------------------------------------------------------------
# 申し込み保存処理（新規登録）
# ------------------------------------------------------------------------------
async def save_application(
    application_id: UUID,
    session: AsyncSession,
    user_id: UUID,
    quote: QuoteSummaryModel,
    request: PensionApplicationRequestModel,
    operator_id: str = None,
    status: str = "pending"
) -> UUID:
    """
    指定見積もりをもとに申込処理を行い、DB登録を行う

    Returns:
        UUID: 登録した見積もりの user_id
    """
    logger.info(f"申し込み保存開始: user_id={user_id}, quote_id={quote.quote_id}")

    if str(quote.user_id) != str(user_id):
        logger.error(f"見積もりのuser_id:{quote.user_id}, リクエストuser_id:{user_id}")
        raise ValueError("他人の見積もりに対して申込処理はできません")
    if quote.contract_date is None:
        logger.error(f"見積もりに契約日が設定されていません quote_id={quote.quote_id}")
        raise ValueError("見積もりに契約日が設定されていません")

    # 型変換
    birth_date = (
        datetime.strptime(quote.birth_date, "%Y-%m-%d").date()
        if isinstance(quote.birth_date, str)
        else quote.birth_date
    )
    contract_date = (
        datetime.strptime(quote.contract_date, "%Y-%m-%d").date()
        if isinstance(quote.contract_date, str)
        else quote.contract_date
    )

    # applications テーブル作成
    application = Application(
        application_id=application_id,
        quote_id=quote.quote_id,
        user_id=user_id,
        application_status=status,
        approved_by = None,
        application_number = None,
        applied_at=datetime.now(),
        created_by=operator_id,
        updated_by=operator_id,
    )

    # application_details テーブル作成（スナップショット）
    detail = ApplicationDetail(
        application_id=application_id,
        birth_date=birth_date,
        gender=quote.gender,
        monthly_premium=quote.monthly_premium,
        payment_period_years=quote.payment_period_years,
        tax_deduction_enabled=quote.tax_deduction_enabled,
        contract_date=contract_date,
        contract_interest_rate=quote.contract_interest_rate,
        total_paid_amount=quote.total_paid_amount,
        pension_start_age=quote.pension_start_age,
        annual_tax_deduction=quote.annual_tax_deduction,
        plan_code=quote.plan_code,
        payment_method = request.payment_method,
        user_consent=True,
        identity_verified = request.identity_verified,
    )

    # DB登録
    session.add_all([application, detail])
    await session.commit()
    logger.info(f"申し込み保存完了: application_id={application_id}")

# ------------------------------------------------------------------------------
# ステータス更新処理
# ------------------------------------------------------------------------------
async def update_application_status(
        session: AsyncSession, 
        application_id: UUID, 
        user_id: UUID, 
        new_status: str
    ):
    """
    見積もりステータスを更新
    """
    logger.info("ステータス更新: application_id=%s, new_state=%s", application_id, new_status)

    result = await session.execute(
        select(Application).where(Application.application_id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(status_code=404, detail="申し込みが存在しません")
    if str(application.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="他人の申し込みは更新できません")

    application.application_status = new_status

    #Commit
    await session.commit()

    return

# ------------------------------------------------------------------------------
# 任意フィールド更新処理
# ------------------------------------------------------------------------------
async def update_application(
    session: AsyncSession,
    application_id: UUID,
    user_id: UUID,
    updates: PensionApplicationRequestModel
) -> PensionApplicationResponseModel:
    logger.info("見積もり更新開始: application_id=%s, user_id=%s", application_id, user_id)

    result = await session.execute(
        select(Application, ApplicationDetail)
        .join(ApplicationDetail)
        .where(Application.application_id == application_id)
    )
    record = result.first()

    if not record:
        raise HTTPException(status_code=404, detail="申し込みが存在しません")

    application, detail = record

    if application.user_id != user_id:
        raise HTTPException(status_code=403, detail="他人の申し込みは更新できません")

    if application.application_status != "pending":
        raise HTTPException(status_code=400, detail="pendingd状態のみ更新可能です")

    detail.user_consent = updates.user_consent
    detail.payment_method = updates.payment_method
    detail.identity_verified = updates.identity_verified

    await session.commit()

    return _build_application_response_model(application, detail, scenarios=[], beneficiaries=[])

# ------------------------------------------------------------------------------
# 保険金受け取り代理人保存（既存削除→上書き保存）
# ------------------------------------------------------------------------------
async def save_beneficiaries_to_mongo(
    mongo_client: AsyncIOMotorClient,
    application_id: str,
    beneficiaries: List[ApplicationBeneficiariesModel]
):
    logger.info("MongoDBシナリオ上書き開始: application_id=%s", application_id)

    db_name = config.mongodb["database"]
    collection_name = config.mongodb["collection"]
    collection = mongo_client[db_name][collection_name]

    try:
        # 既存データを削除
        delete_result = await collection.delete_many({"application_id": str(application_id)})
        logger.info(f"[MongoDB] 既存削除完了 (deleted_count={delete_result.deleted_count})")

        # 登録用データに変換
        now = datetime.utcnow()
        insert_docs = [
            {
                "application_id": str(application_id),
                "beneficiaries": [b.dict() for b in beneficiaries],
                "updated_at": now,
            }
        ]

        # MongoDBに一括挿入
        if insert_docs:
            insert_result = await collection.insert_many(insert_docs)
            logger.info(f"[MongoDB] 保険金受取人情報を登録 (inserted_count={len(insert_result.inserted_ids)})")
        else:
            logger.warning("[MongoDB] 登録対象の受取人情報が空のためスキップ")

    except Exception as e:
        logger.exception(f"[MongoDB] 保険金受取人情報の保存中にエラー発生: {e}")
        raise

# ------------------------------------------------------------------------------
# シナリオ保存（既存削除→上書き保存）
# ------------------------------------------------------------------------------
async def save_scenarios_to_mongo(
    mongo_client: AsyncIOMotorClient,
    application_id: str,
    scenarios: List[QuoteScenarioModel]
):
    logger.info("MongoDBシナリオ上書き開始: application_id=%s", application_id)

    db_name = config.mongodb["database"]
    collection_name = config.mongodb["scenario_collection"]
    collection = mongo_client[db_name][collection_name]

    try:
        # 既存データを削除
        delete_result = await collection.delete_many({"application_id": str(application_id)})
        logger.info(f"[MongoDB] 既存削除完了 (deleted_count={delete_result.deleted_count})")

        scenario_docs = []
        for scenario in scenarios:
            doc = scenario.model_dump(mode="json")

            # MongoDB用のメタデータ追加
            doc["application_id"] = str(application_id)
            doc["logged_at"] = datetime.utcnow()

            # セット形式の異常値を検出し修正（過去の変換バグ対策）
            if isinstance(doc.get("scenario_type"), set):
                scenario_type_set = doc["scenario_type"]
                if len(scenario_type_set) == 1:
                    doc["scenario_type"] = next(iter(scenario_type_set))
                else:
                    logger.error("scenario_typeが不正（複数のset）: %s", scenario_type_set)
                    continue  # このレコードはスキップ

            scenario_docs.append(doc)

        if scenario_docs:
            await collection.insert_many(scenario_docs)
            logger.info("MongoDBシナリオ上書き完了: 件数=%d", len(scenario_docs))
        else:
            logger.warning("保存対象のシナリオが空のためMongoDBへの保存をスキップ")

    except Exception as e:
        logger.exception(f"[MongoDB] 保険金受取人情報の保存中にエラー発生: {e}")
        raise

# ------------------------------------------------------------------------------
# 内部: Applicationレスポンスモデル組み立て
# ------------------------------------------------------------------------------
def _build_application_response_model(
    application: Application,
    detail: ApplicationDetail,
    scenarios: List[PensionApplicationScenarioModel],
    beneficiaries: List[ApplicationBeneficiariesModel],
) -> PensionApplicationResponseModel:
    """
    Application + ApplicationDetail を統合してレスポンスモデルに変換
    """
    return PensionApplicationResponseModel(
        # --- applications テーブル ---
        application_id=application.application_id,
        quote_id=application.quote_id,
        user_id=application.user_id,
        application_status=application.application_status,
        user_consent=detail.user_consent,
        payment_method=detail.payment_method,
        identity_verified=detail.identity_verified,
        approved_by=application.approved_by,
        approval_date=application.approval_date,
        application_number=application.application_number,
        applied_at=application.applied_at,
        updated_at=application.updated_at,
        created_by=application.created_by,
        updated_by=application.updated_by,

        # --- application_details テーブル ---
        birth_date=detail.birth_date,
        gender=detail.gender,
        monthly_premium=detail.monthly_premium,
        payment_period_years=detail.payment_period_years,
        tax_deduction_enabled=detail.tax_deduction_enabled,
        contract_date=detail.contract_date,
        contract_interest_rate=float(detail.contract_interest_rate),
        total_paid_amount=detail.total_paid_amount,
        pension_start_age=detail.pension_start_age,
        annual_tax_deduction=detail.annual_tax_deduction,
        plan_code=detail.plan_code,
        detail_payment_method=detail.payment_method,

        # --- MongoDB ---
        scenarios=scenarios,
        beneficiaries=beneficiaries
    )