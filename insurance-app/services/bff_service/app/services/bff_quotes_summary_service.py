# -*- coding: utf-8 -*-
"""
/bff/my/quotes-summary 用サービスロジック

- 見積もり一覧を取得し、ステータス別にサマリーを構築する
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import httpx
from typing import List
from datetime import datetime
from app.model.bff_quotes_summary import QuoteSummaryResponseModel

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

QUOTES_URL = config.quotation_service["base_url"] + config.quotation_service["get_path"]

# ------------------------------------------------------------------------------
# サービスロジック
# ------------------------------------------------------------------------------
async def fetch_quote_summary(access_token: str) -> QuoteSummaryResponseModel:
    """
    見積もり一覧からサマリー情報を集約する
    """
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(QUOTES_URL, headers=headers)
            resp.raise_for_status()
            quotes = resp.json()
    except Exception as e:
        logger.exception("見積もり一覧取得失敗")
        raise

    total_count = len(quotes)
    draft_count = 0
    confirmed_count = 0
    applied_count = 0
    cancelled_count = 0
    latest_created_at = None

    for q in quotes:
        state = q.get("quote_state")
        if state == "draft":
            draft_count += 1
        elif state == "confirmed":
            confirmed_count += 1
        elif state == "applied":
            applied_count += 1
        elif state == "cancelled":
            cancelled_count += 1

        created_at_str = q.get("created_at")
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str)
                if latest_created_at is None or created_at > latest_created_at:
                    latest_created_at = created_at
            except Exception:
                logger.warning(f"created_atの解析に失敗: {created_at_str}")

    return QuoteSummaryResponseModel(
        total_count=total_count,
        latest_created_at=latest_created_at,
        draft_count=draft_count,
        confirmed_count=confirmed_count,
        applied_count=applied_count,
        cancelled_count=cancelled_count
    )