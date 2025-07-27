# -*- coding: utf-8 -*-
"""
/bff/my/quotes-summary 用レスポンスモデル定義
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QuoteSummaryResponseModel(BaseModel):
    total_count: int = Field(..., description="見積もり総件数")
    latest_created_at: Optional[datetime] = Field(None, description="最新作成日時")
    draft_count: int = Field(..., description="下書き状態の見積もり数")
    confirmed_count: int = Field(..., description="確定状態の見積もり数")
    applied_count: int = Field(..., description="申込済み状態の見積もり数")
    cancelled_count: int = Field(..., description="キャンセルされた見積もり数")