# -*- coding: utf-8 -*-
"""
/bff/my/contracts-summary 用サービスロジック

- ユーザー契約情報を取得し、状態別に件数をサマリー集計する
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import httpx
from app.model.bff_contracts_summary import ContractSummaryResponseModel

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

CONTRACTS_URL = config.contraction_service["base_url"] + config.contraction_service["get_path"]

# ------------------------------------------------------------------------------
# サービスロジック
# ------------------------------------------------------------------------------
async def fetch_contract_summary(access_token: str) -> ContractSummaryResponseModel:
    """
    契約一覧を取得し、ステータス別に件数を集計して返す
    """
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(CONTRACTS_URL, headers=headers)
            resp.raise_for_status()
            contracts = resp.json()
    except Exception as e:
        logger.exception("契約情報取得失敗")
        raise

    total_count = len(contracts)
    active_count = 0
    expired_count = 0
    cancelled_count = 0

    for c in contracts:
        status = c.get("contract_status")
        if status == "active":
            active_count += 1
        elif status == "expired":
            expired_count += 1
        elif status == "cancelled":
            cancelled_count += 1

    return ContractSummaryResponseModel(
        total_count=total_count,
        active_count=active_count,
        expired_count=expired_count,
        cancelled_count=cancelled_count
    )