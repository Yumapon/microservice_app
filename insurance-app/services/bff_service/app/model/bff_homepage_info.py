# -*- coding: utf-8 -*-
"""
/bff/public/homepage-info 用レスポンスモデル定義
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class FeaturedPlanModel(BaseModel):
    plan_id: str = Field(..., description="保険プランID")
    name: str = Field(..., description="保険商品名")
    category: str = Field(..., description="カテゴリ（例: 医療保険）")
    description: str = Field(..., description="紹介文")
    image_url: Optional[str] = Field(None, description="画像URL")
    monthly_premium: Optional[int] = Field(None, description="月額保険料")


class CampaignModel(BaseModel):
    campaign_id: str = Field(..., description="キャンペーンID")
    title: str = Field(..., description="キャンペーン名")
    description: str = Field(..., description="キャンペーン内容")
    image_url: Optional[str] = Field(None, description="キャンペーン画像URL")
    valid_until: Optional[str] = Field(None, description="終了日（ISO 8601）")


class HomepageInfoResponseModel(BaseModel):
    featured_plans: List[FeaturedPlanModel] = Field(..., description="トップに表示する保険商品")
    campaigns: List[CampaignModel] = Field(..., description="キャンペーン情報一覧（現在はmock）")