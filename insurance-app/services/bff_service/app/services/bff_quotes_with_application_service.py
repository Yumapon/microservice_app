# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import asyncio
import httpx

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

async def fetch_quotes_with_application(access_token: str) -> list:
    """
    見積もり一覧と申込一覧を取得し、quote_id をキーに合成する
    Returns:
        List[dict]: QuoteWithApplicationModel に準拠した構造のリスト
    """
    quotation_url = f"{config.quotation_service['base_url']}/api/v1/my/quotes"
    application_url = f"{config.application_service['base_url']}/api/v1/my/applications"
    headers = {"Authorization": f"Bearer {access_token}"}

    async with httpx.AsyncClient() as client:
        quote_resp, app_resp = await asyncio.gather(
            client.get(quotation_url, headers=headers),
            client.get(application_url, headers=headers),
        )

    if quote_resp.status_code != 200 or app_resp.status_code != 200:
        logger.error(f"[BFF] サービス呼び出し失敗: quote={quote_resp.status_code}, app={app_resp.status_code}")
        raise Exception("外部サービス呼び出しに失敗")

    quotes = quote_resp.json()
    applications = app_resp.json()
    logger.debug(f"[BFF] 取得件数: quotes={len(quotes)}, applications={len(applications)}")

    app_map = {app["quote_id"]: app for app in applications}
    result = []

    for quote in quotes:
        application = app_map.get(quote["quote_id"])
        result.append({
            "quote_id": quote["quote_id"],
            "quote_state": quote["quote_state"],
            "created_at": quote["created_at"],
            "contract_conditions": {
                "birth_date": quote["birth_date"],
                "gender": quote["gender"],
                "monthly_premium": quote["monthly_premium"],
                "payment_period_years": quote["payment_period_years"],
                "tax_deduction_enabled": quote["tax_deduction_enabled"],
                "pension_payment_years": quote["pension_payment_years"],
                "plan_code": quote["plan_code"],
            },
            "calculation_result": {
                "contract_date": quote["contract_date"],
                "contract_interest_rate": quote["contract_interest_rate"],
                "total_paid_amount": quote["total_paid_amount"],
                "pension_start_age": quote["pension_start_age"],
                "annual_tax_deduction": quote["annual_tax_deduction"],
            },
            "application": {
                "application_id": application["application_id"],
                "application_status": application["application_status"],
                "application_number": application.get("application_number"),
                "applied_at": application["applied_at"],
                "payment_method": application["payment_method"],
                "user_consent": application["user_consent"],
                "identity_verified": application["identity_verified"],
            } if application else None
        })

    logger.info(f"[BFF] 合成完了。返却件数: {len(result)}")
    return result