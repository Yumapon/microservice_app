from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

from app.db_models.contracts import Contract
from app.models.contracts import ContractCreateModel
from app.models.beneficiaries import ContractBeneficiariesModel
from app.models.scenarios import PensionQuoteScenarioModel
from app.config.config import Config
from app.services.mongo_helpers import (
    get_scenarios_by_application_id,
    get_application_beneficiaries_by_application_id,
    save_contract_beneficiaries
)

from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)
config = Config()


async def create_contract(
    session: AsyncSession,
    mongo_client: AsyncIOMotorClient,
    contract_input: ContractCreateModel,
) -> UUID:
    """
    契約を PostgreSQL に保存し、MongoDB に受取人情報を保存する

    Parameters:
        session (AsyncSession): SQLAlchemyの非同期セッション
        mongo_client (AsyncIOMotorClient): MongoDBクライアント
        contract_input (ContractCreateModel): 契約作成用のスナップショット情報

    Returns:
        UUID: 作成された契約ID
    """
    contract_id = contract_input.contract_id
    logger.info(f"[Contract] 契約作成開始 contract_id={contract_id}")

    # --- PostgreSQL への登録 ---
    new_contract = Contract(
        contract_id=contract_id,
        application_id=contract_input.application_id,
        quote_id=contract_input.quote_id,
        user_id=contract_input.user_id,
        gender=contract_input.gender,
        birth_date=contract_input.birth_date,
        monthly_premium=contract_input.monthly_premium,
        payment_period_years=contract_input.payment_period_years,
        pension_payment_years=contract_input.pension_payment_years,
        tax_deduction_enabled=contract_input.tax_deduction_enabled,
        contract_date=contract_input.contract_date,
        contract_interest_rate=contract_input.contract_interest_rate,
        total_amount_paid=contract_input.total_amount_paid,
        total_amount_returned=contract_input.total_amount_returned,
        refund_rate=contract_input.refund_rate,
        tax_deduction_amount=contract_input.tax_deduction_amount,
        user_consent=contract_input.user_consent,
        applied_at=contract_input.applied_at,
        created_by=contract_input.created_by,
        updated_by=contract_input.created_by,
    )

    session.add(new_contract)
    await session.commit()

    # --- MongoDBから受取人情報を取得 ---
    app_beneficiaries = await get_application_beneficiaries_by_application_id(
        mongo_client,
        application_id=contract_input.application_id
    )

    if not app_beneficiaries:
        logger.warning(f"[Contract] 受取人情報が見つかりませんでした application_id={contract_input.application_id}")
        raise HTTPException(status_code=400, detail="受取人情報が存在しません")

    # --- MongoDBに保存（contract_idに紐づける） ---
    contract_beneficiaries_doc = ContractBeneficiariesModel(
        contract_id=contract_id,
        beneficiaries=app_beneficiaries.beneficiaries,
        updated_at=datetime.utcnow()
    )

    await save_contract_beneficiaries(mongo_client, contract_beneficiaries_doc)

    logger.info(f"[Contract] 契約および受取人情報の登録完了 contract_id={contract_id}")
    return contract_id