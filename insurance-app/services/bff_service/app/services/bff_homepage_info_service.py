# -*- coding: utf-8 -*-
"""
/bff/public/homepage-info 用サービスロジック

- 公開保険商品情報とキャンペーン情報（mock）を取得・構築する
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import httpx
from app.model.bff_homepage_info import (
    HomepageInfoResponseModel,
    FeaturedPlanModel,
    CampaignModel
)

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

PLANS_URL = config.plans_service["base_url"] + config.plans_service["get_path"]

# ------------------------------------------------------------------------------
# サービスロジック
# ------------------------------------------------------------------------------
async def fetch_homepage_info() -> HomepageInfoResponseModel:
    """
    トップページで使用する情報を集約
    - 保険紹介一覧（public_plans_service）
    - キャンペーン情報（現状はmock）
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(PLANS_URL)
            resp.raise_for_status()
            plans = resp.json()
    except Exception as e:
        logger.warning(f"保険紹介取得失敗: {e}")
        plans = []

    featured_plans = [
        FeaturedPlanModel(
            plan_id=plan.get("plan_id", ""),
            name=plan.get("name", ""),
            category=plan.get("category", ""),
            description=plan.get("description", ""),
            image_url=plan.get("image_url"),
            monthly_premium=plan.get("monthly_premium")
        )
        for plan in plans[:5]  # 最大5件に制限（仮）
    ]

    # --- mockキャンペーン（将来 DB/API から取得に差し替え予定）---
    campaigns = [
        CampaignModel(
            campaign_id="cmp001",
            title="夏の加入キャンペーン",
            description="今だけ！最大2ヶ月分の保険料が無料！",
            image_url="https://example.com/images/campaign_summer.png",
            valid_until="2025-08-31"
        )
    ]

    return HomepageInfoResponseModel(
        featured_plans=featured_plans,
        campaigns=campaigns
    )