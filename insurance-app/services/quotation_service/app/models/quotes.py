# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりに使用するリクエスト・レスポンス・シナリオ・ステータス更新モデル
- API入出力用スキーマ
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from datetime import date, datetime
from uuid import UUID
from typing import List, Literal, Optional

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
    pension_duration_years: conint(ge=5, le=30) = Field(..., description="年金受取期間（5〜30年）")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無（True/False）")

# ------------------------------------------------------------------------------
# 利率シナリオモデル（内部構造）
# ------------------------------------------------------------------------------
class PensionQuoteScenarioModel(BaseModel):
    """
    利率シナリオごとの見積もり結果モデル
    一つの見積もりに対して複数のシナリオを保持
    """
    quote_id: UUID = Field(..., description="見積もりID（PostgreSQL連携用）")
    scenario_type: Literal["base", "high", "low"] = Field(..., description="シナリオ種別")
    interest_rate: float = Field(..., description="利率（%）")
    estimated_pension: int = Field(..., description="想定年金額（例：10年分割合計）")
    refund_rate: float = Field(..., description="15年払込時点の返戻率（%）")
    refund_on_15_years: int = Field(..., description="15年払込時点の返戻金（円）")
    lump_sum_amount: int = Field(..., description="一括受取額（円）")
    note: Optional[str] = Field(None, description="補足情報（任意）")
    created_at: Optional[datetime] = Field(None, description="MongoDB側の作成日時")
    updated_at: Optional[datetime] = Field(None, description="MongoDB側の更新日時")

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