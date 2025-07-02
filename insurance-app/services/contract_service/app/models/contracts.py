# -*- coding: utf-8 -*-
"""
契約情報に使用するリクエスト・レスポンス・DBモデル定義
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from datetime import datetime, date
from typing import Literal, List
from pydantic import BaseModel, Field

# ------------------------------------------------------------------------------
# 内部モデル（利率シナリオの1件分）
# ------------------------------------------------------------------------------
class ContractScenarioModel(BaseModel):
    """
    利率シナリオごとの契約情報モデル
    契約に基づく返戻金・利率のシミュレーション結果（複数シナリオ）
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
class ContractResponseModel(BaseModel):
    """
    契約情報応答モデル
    フロントエンドに返却するための出力データ。
    契約詳細または一覧取得で利用される。
    """
    contract_id: str = Field(..., description="契約ID（UUID）")
    user_id: str = Field(..., description="ユーザーID（UUID）")
    application_id: str = Field(..., description="紐づく申込ID（UUID）")
    quote_id: str = Field(..., description="紐づく見積もりID（UUID）")
    contract_status: Literal['active', 'cancelled'] = Field(..., description="契約ステータス（active または cancelled）")

    user_consent: bool = Field(..., description="契約時のユーザー同意フラグ")
    applied_at: datetime = Field(..., description="契約確定日時")

    birth_date: date = Field(..., description="契約者の生年月日")
    gender: Literal["男", "女"] = Field(..., description="性別（'男' または '女'）")
    monthly_premium: int = Field(..., description="月額保険料（円）")
    payment_period_years: int = Field(..., description="払込期間（年数）")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無")

    contract_date: date = Field(..., description="契約開始日")
    contract_interest_rate: float = Field(..., description="契約時利率（%）")
    total_paid_amount: int = Field(..., description="総払込額（円）")
    pension_start_age: int = Field(..., description="年金受給開始年齢")
    annual_tax_deduction: int = Field(..., description="年間税控除額（円）")

    scenarios: List[ContractScenarioModel] = Field(..., description="利率シナリオごとの契約見積結果")

    created_at: datetime = Field(..., description="契約作成日時")
    cancelled_at: datetime | None = Field(None, description="解約日時（キャンセルされた場合）")

# ------------------------------------------------------------------------------
# 入力モデル（契約確定用：申込ID指定）
# ------------------------------------------------------------------------------
class ContractCreateRequestModel(BaseModel):
    """
    契約確定のための入力モデル
    申込情報に基づいて契約を新規作成する際に使用
    """
    application_id: str = Field(..., description="契約作成対象の申込ID（UUID）")

# ------------------------------------------------------------------------------
# 更新モデル（契約条件・シナリオの変更）
# ------------------------------------------------------------------------------
class ContractUpdateModel(BaseModel):
    """
    契約情報の更新用リクエストモデル
    必要なフィールドのみ指定（部分更新）
    """
    monthly_premium: int | None = Field(None, description="月額保険料（円）")
    payment_period_years: int | None = Field(None, description="払込期間（年数）")
    tax_deduction_enabled: bool | None = Field(None, description="税制適格特約の有無")
    contract_date: date | None = Field(None, description="契約開始日")
    contract_interest_rate: float | None = Field(None, description="契約時利率（%）")
    total_paid_amount: int | None = Field(None, description="総払込額（円）")
    pension_start_age: int | None = Field(None, description="年金受給開始年齢")
    annual_tax_deduction: int | None = Field(None, description="年間税控除額（円）")
    scenarios: List[ContractScenarioModel] | None = Field(None, description="利率シナリオ一覧")
