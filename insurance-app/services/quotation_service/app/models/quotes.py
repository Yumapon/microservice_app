# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりに使用するリクエスト・レスポンスモデル定義
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from datetime import datetime
from typing import Literal, List

from pydantic import BaseModel, Field, conint

# ------------------------------------------------------------------------------
# 入力モデル（フロントエンド → バックエンド）
# ------------------------------------------------------------------------------
class PensionQuoteRequestModel(BaseModel):
    """
    個人年金保険の見積もり要求モデル
    """
    birth_date: datetime = Field(..., description="契約者の生年月日")
    gender: Literal["男", "女"] = Field(..., description="性別")
    monthly_premium: conint(ge=10000, le=50000, multiple_of=1000) = Field(
        ..., description="月額保険料（¥10,000〜¥50,000）"
    )
    payment_period_years: conint(ge=15, le=45) = Field(
        ..., description="払込期間（15年以上、65歳まで）"
    )
    tax_deduction_enabled: bool = Field(..., description="個人年金保険料税制適格特約の有無")

# ------------------------------------------------------------------------------
# 内部モデル（利率シナリオの1件分）
# ------------------------------------------------------------------------------
class PensionQuoteScenarioModel(BaseModel):
    """
    利率シナリオごとの見積もり結果モデル
    """
    scenario_name: str = Field(..., description="シナリオ名（高金利、標準、最低保証）")
    assumed_interest_rate: float = Field(..., description="想定予定利率")
    total_refund_amount: int = Field(..., description="累計額（最終受取額）")
    annual_annuity: int = Field(..., description="年金の年額")
    lump_sum_amount: int = Field(..., description="一括受取額")
    refund_on_15_years: int = Field(..., description="15年払込時の返戻額")
    refund_rate_on_15_years: float = Field(..., description="返戻率（%）")

# ------------------------------------------------------------------------------
# 出力モデル（バックエンド → フロントエンド）
# ------------------------------------------------------------------------------
class PensionQuoteResponseModel(BaseModel):
    """
    個人年金保険の見積もり応答モデル
    """
    quote_id: str  # 一意の見積もりID
    user_id: str #user id
    contract_date: datetime  # 契約開始日
    contract_interest_rate: float  # 契約時利率（標準シナリオに使用）
    total_paid_amount: int  # 総払込額
    payment_period_years: int  # 払込期間（年数）
    pension_start_age: int  # 年金開始年齢
    annual_tax_deduction: int  # 年間の税控除額（最大）
    scenarios: List[PensionQuoteScenarioModel]  # 各利率シナリオの見積もり結果