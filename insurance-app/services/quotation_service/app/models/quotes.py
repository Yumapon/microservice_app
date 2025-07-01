# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりに使用するリクエスト・レスポンス・DBモデル定義
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from datetime import datetime, date
from typing import Literal, List

from pydantic import BaseModel, Field, conint

# ------------------------------------------------------------------------------
# 入力モデル（フロントエンド → バックエンド）
# ------------------------------------------------------------------------------
class PensionQuoteRequestModel(BaseModel):
    """
    個人年金保険の見積もり要求モデル
    フロントエンドからバックエンドに送信される入力データ。
    DB保存に必要な情報の一部（ユーザーID、契約日など）は含まない。
    """
    birth_date: datetime = Field(..., description="契約者の生年月日（datetime型）")
    gender: Literal["男", "女"] = Field(..., description="性別（'男' または '女'）")
    monthly_premium: conint(ge=10000, le=50000, multiple_of=1000) = Field(
        ..., description="月額保険料（¥10,000〜¥50,000の範囲で1,000円単位）"
    )
    payment_period_years: conint(ge=15, le=45) = Field(
        ..., description="払込期間（15〜45年）"
    )
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無（True/False）")

# ------------------------------------------------------------------------------
# 内部モデル（利率シナリオの1件分）
# ------------------------------------------------------------------------------
class PensionQuoteScenarioModel(BaseModel):
    """
    利率シナリオごとの見積もり結果モデル
    一つの見積もりに対して複数のシナリオ（高金利、標準、最低保証）を保持。
    DBでは JSONB 配列として保存される。
    """
    scenario_name: str = Field(..., description="シナリオ名（高金利、標準、最低保証など）")
    assumed_interest_rate: float = Field(..., description="想定される予定利率（%）")
    total_refund_amount: int = Field(..., description="累計返戻金額（最終受取額）")
    annual_annuity: int = Field(..., description="年金形式で受け取る場合の年間受取額")
    lump_sum_amount: int = Field(..., description="一括受取額")
    refund_on_15_years: int = Field(..., description="15年間払込んだ場合の返戻金額")
    refund_rate_on_15_years: float = Field(..., description="15年間払込んだ場合の返戻率（%）")

# ------------------------------------------------------------------------------
# 出力モデル（バックエンド → フロントエンド）
# ------------------------------------------------------------------------------
class PensionQuoteResponseModel(BaseModel):
    """
    個人年金保険の見積もり応答モデル
    フロントエンドに返却するための出力データ。
    ユーザーに必要な情報のみに限定して構成されており、DB内部の状態（quote_state など）は含まない。
    """
    quote_id: str = Field(..., description="見積もりID（UUID）")
    user_id: str = Field(..., description="ユーザーID（UUID）")
    contract_date: datetime = Field(..., description="契約開始日（datetime型）")
    contract_interest_rate: float = Field(..., description="契約時利率（%）")
    total_paid_amount: int = Field(..., description="総払込額（円）")
    payment_period_years: int = Field(..., description="払込期間（年数）")
    pension_start_age: int = Field(..., description="年金受給開始年齢")
    annual_tax_deduction: int = Field(..., description="年間税控除額（最大値）")
    scenarios: List[PensionQuoteScenarioModel] = Field(..., description="利率シナリオの見積もり結果一覧")

# ------------------------------------------------------------------------------
# ステータス更新モデル（quote_state の更新用）
# ------------------------------------------------------------------------------
class QuoteStateUpdateModel(BaseModel):
    """
    見積もりのステータス（quote_state）を更新するためのリクエストモデル
    許可されるステータスは 'none', 'applied', 'reverted', 'cancelled' のみ
    """
    new_state: Literal['none', 'applied', 'reverted', 'cancelled'] = Field(
        ..., description="更新後のステータス（quote_state）"
    )