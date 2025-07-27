# -*- coding: utf-8 -*-
"""
/bff/my/contracts-summary 用レスポンスモデル定義
"""

from pydantic import BaseModel, Field


class ContractSummaryResponseModel(BaseModel):
    total_count: int = Field(..., description="契約全体の件数")
    active_count: int = Field(..., description="アクティブ契約数")
    expired_count: int = Field(..., description="満期終了契約数")
    cancelled_count: int = Field(..., description="契約解除件数")