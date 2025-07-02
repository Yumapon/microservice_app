# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりに使用するリクエスト・レスポンス・シナリオ・ステータス更新モデル
- API入出力用スキーマ
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from datetime import date
from uuid import UUID
from typing import List, Literal

from pydantic import BaseModel, Field, conint

# ------------------------------------------------------------------------------
# 入力モデル（フロントエンド → バックエンド）
# ------------------------------------------------------------------------------
class PensionQuoteRequestModel(BaseModel):
    """
    個人年金保険の見積もり要求モデル
    フロントエンドから送信される入力データ
    """
    birth_date: date = Field(..., description="契約者の生年月日（date型）")
    gender: Literal["男", "女"] = Field(..., description="性別（'男' または '女'）")
    monthly_premium: conint(ge=10000, le=50000, multiple_of=1000) = Field(
        ..., description="月額保険料（¥10,000〜¥50,000の範囲で1,000円単位）"
    )
    payment_period_years: conint(ge=15, le=45) = Field(
        ..., description="払込期間（15〜45年）"
    )
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無（True/False）")

# ------------------------------------------------------------------------------
# 利率シナリオモデル（内部構造）
# ------------------------------------------------------------------------------
class PensionQuoteScenarioModel(BaseModel):
    """
    利率シナリオごとの見積もり結果モデル
    一つの見積もりに対して複数のシナリオを保持
    """
    scenario_name: str = Field(..., description="シナリオ名（高金利、標準、最低保証など）")
    assumed_interest_rate: float = Field(..., description="想定利率（%）")
    total_refund_amount: int = Field(..., description="累計返戻金額（円）")
    annual_annuity: int = Field(..., description="年金受取時の年間金額（円）")
    lump_sum_amount: int = Field(..., description="一括受取額（円）")
    refund_on_15_years: int = Field(..., description="15年払込時点の返戻金額（円）")
    refund_rate_on_15_years: float = Field(..., description="15年払込時点の返戻率（%）")

# ------------------------------------------------------------------------------
# 出力モデル（バックエンド → フロントエンド）
# ------------------------------------------------------------------------------
class PensionQuoteResponseModel(BaseModel):
    """
    個人年金保険の見積もり応答モデル
    フロントエンドに返却するための出力データ
    """
    quote_id: UUID = Field(..., description="見積もりID（UUID）")
    contract_date: date = Field(..., description="契約開始日")
    contract_interest_rate: float = Field(..., description="契約時利率（%）")
    total_paid_amount: int = Field(..., description="総払込額（円）")
    payment_period_years: int = Field(..., description="払込期間（年）")
    pension_start_age: int = Field(..., description="年金受給開始年齢")
    annual_tax_deduction: int = Field(..., description="年間税控除額（円）")
    scenarios: List[PensionQuoteScenarioModel] = Field(..., description="利率シナリオ一覧")

# ------------------------------------------------------------------------------
# ステータス更新モデル（quote_stateの更新）
# ------------------------------------------------------------------------------
class QuoteStateUpdateModel(BaseModel):
    """
    見積もりステータス更新モデル
    """
    new_state: Literal['none', 'applied', 'reverted', 'cancelled'] = Field(
        ..., description="更新後の見積もりステータス"
    )