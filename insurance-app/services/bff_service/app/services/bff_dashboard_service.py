# -*- coding: utf-8 -*-
"""
/bff/my/dashboard 用サービスロジック

- 各サービスのユーザー個別情報（見積・申込・契約）を集約して返す
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import httpx
import asyncio
from app.model.bff_dashboard import (
    DashboardResponseModel,
    QuoteModel,
    QuoteScenarioModel,
    ApplicationModel,
    ApplicationScenarioModel,
    ContractModel
)

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

# エンドポイント定義
QUOTES_URL = config.quotation_service["base_url"] + config.quotation_service["get_path"]
APPLICATIONS_URL = config.application_service["base_url"] + config.application_service["get_path"]
CONTRACTS_URL = config.contraction_service["base_url"] + config.contraction_service["get_path"]

# ------------------------------------------------------------------------------
# サービスロジック
# ------------------------------------------------------------------------------
async def fetch_user_dashboard(access_token: str) -> DashboardResponseModel:
    """
    ユーザー個別の見積もり・申込・契約を一括取得する
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        try:
#            quote_resp, app_resp, contract_resp = await asyncio.gather(
#                client.get(QUOTES_URL, headers=headers),
#                client.get(APPLICATIONS_URL, headers=headers),
#                client.get(CONTRACTS_URL, headers=headers)
#            )
            quote_resp, app_resp= await asyncio.gather(
                client.get(QUOTES_URL, headers=headers),
                client.get(APPLICATIONS_URL, headers=headers)
            )
        except Exception as e:
            logger.exception("外部API呼び出し失敗")
            raise

    # 見積もりの整形
    quotes = []
    try:
        quotes_raw = quote_resp.json()
        for item in quotes_raw:
            quotes.append(
                QuoteModel(
                    quote_id=item["quote_id"],
                    quote_state=item["quote_state"],
                    plan_code=item.get("plan_code", ""),
                    monthly_premium=item["monthly_premium"],
                    payment_period_years=item["payment_period_years"],
                    contract_date=item["contract_date"],
                    created_at=item["created_at"],
                    scenarios=[
                        QuoteScenarioModel(
                            scenario_type=sc["scenario_type"],
                            interest_rate=sc["interest_rate"],
                            estimated_pension=sc["estimated_pension"],
                            annual_pension=sc["annual_pension"],
                            lump_sum_amount=sc["lump_sum_amount"],
                            created_at=sc["created_at"]
                        ) for sc in item.get("scenarios", [])
                    ]
                )
            )
    except Exception as e:
        logger.warning(f"見積もりパース失敗: {e}")

    # 申込の整形
    applications = []
    try:
        applications_raw = app_resp.json()
        for item in applications_raw:
            applications.append(
                ApplicationModel(
                    application_id=item["application_id"],
                    quote_id=item["quote_id"],
                    application_status=item["application_status"],
                    monthly_premium=item["monthly_premium"],
                    contract_date=item["contract_date"],
                    plan_code=item["plan_code"],
                    applied_at=item["applied_at"],
                    scenarios=[
                        ApplicationScenarioModel(
                            scenario_type=sc["scenario_type"],
                            interest_rate=sc["interest_rate"],
                            estimated_pension=sc["estimated_pension"],
                            annual_pension=sc["annual_pension"],
                            lump_sum_amount=sc["lump_sum_amount"],
                            created_at=sc["created_at"]
                        ) for sc in item.get("scenarios", [])
                    ]
                )
            )
    except Exception as e:
        logger.warning(f"申込パース失敗: {e}")

    # 契約の整形（未実装前提）
#    contracts = []
#    try:
#        contracts_raw = contract_resp.json()
#        for item in contracts_raw:
#            contracts.append(
#                ContractModel(
#                    contract_id=item["contract_id"],
#                    quote_id=item["quote_id"],
#                    application_id=item["application_id"],
#                    plan_code=item["plan_code"],
#                    monthly_premium=item["monthly_premium"],
#                    contract_date=item["contract_date"],
#                    contract_status=item["contract_status"]
#                )
#            )
    except Exception as e:
        logger.warning(f"契約パース失敗: {e}")

    return DashboardResponseModel(
        quotes=quotes,
        applications=applications,
        #contracts=contracts,
        contracts=[],
        unread_notifications=0  # 通知は未実装
    )