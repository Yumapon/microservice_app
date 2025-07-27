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
from enum import Enum

from pydantic import BaseModel, Field, conint, constr

# ------------------------------------------------------------------------------
# 入力モデル（フロントエンド → バックエンド）
# ------------------------------------------------------------------------------
class PensionQuoteRequestModel(BaseModel):
    """
    個人年金保険の見積もり要求モデル
    フロントエンドから送信される入力データ
    """
    birth_date: date = Field(..., description="契約者の生年月日（date型）")
    gender: Literal["male", "female"] = Field(..., description="性別（'male' または 'female'）")
    monthly_premium: conint(ge=10000, le=50000, multiple_of=1000) = Field(
        ..., description="月額保険料（¥10,000〜¥50,000の範囲で1,000円単位）"
    )
    payment_period_years: conint(ge=15, le=45) = Field(
        ..., description="払込期間（15〜45年）"
    )
    pension_payment_years: conint(ge=5, le=30) = Field(..., description="年金受取期間（5〜30年）")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無（True/False）")

# ------------------------------------------------------------------------------
# 利率シナリオモデル（MongoDBへ格納するデータ）
# ------------------------------------------------------------------------------
class PensionQuoteScenarioModel(BaseModel):
    """
    利率シナリオごとの見積もり結果モデル
    一つの見積もりに対して複数のシナリオ（base, low, high）を保持
    MongoDBに保存される構造に準拠
    """
    quote_id: UUID = Field(..., description="見積もりID（PostgreSQL連携用）")
    scenario_type: Literal["base", "high", "low"] = Field(..., description="シナリオ種別")
    interest_rate: float = Field(..., description="シナリオ利率（%）")

    estimated_pension: int = Field(..., description="年金累計額（年額 × 年数）")
    pension_refund_rate: float = Field(..., description="年金累計額の返戻率（%）")
    annual_pension: int = Field(..., description="年間年金額（想定）")

    lump_sum_amount: int = Field(..., description="一括受取額（円）")
    lump_sum_refund_rate: float = Field(..., description="一括受取額の返戻率（%）")

    refund_on_15_years: int = Field(..., description="15年払込時点の解約返戻金額（円）")
    refund_rate: float = Field(..., description="15年払込時点の返戻率（%）")

    note: Optional[str] = Field(None, description="補足情報（任意）")
    created_at: Optional[datetime] = Field(None, description="MongoDB側の作成日時")
    updated_at: Optional[datetime] = Field(None, description="MongoDB側の更新日時")

# ------------------------------------------------------------------------------
# 保険計算の結果を返却するモデル
# ------------------------------------------------------------------------------
class PensionQuoteCalculateResult(BaseModel):
    quote_id: UUID
    contract_date: date
    contract_interest_rate: float
    total_paid_amount: int
    pension_start_age: int
    annual_tax_deduction: int
    scenarios: List[PensionQuoteScenarioModel]

# ------------------------------------------------------------------------------
# ステータス更新モデル
# ------------------------------------------------------------------------------
class QuoteState(str, Enum):
    """
    見積もりのステータス列挙型
    - confirmed: 確定済
    - applied: 申込済
    - cancelled: キャンセル済
    - expired: 有効期限切れ
    """
    confirmed = "confirmed"
    applied = "applied"
    cancelled = "cancelled"
    expired = "expired"

class PensionQuoteResponseModel(BaseModel):
    """
    個人年金保険の見積もり応答モデル（PostgreSQL + MongoDB統合）
    - quotes + quote_details + MongoDBシナリオを統合した完全レスポンス
    """

    # --- quotesテーブル項目 ---
    quote_id: UUID = Field(..., description="見積もりID（UUID）")
    user_id: UUID = Field(..., description="ユーザーID（UUID）")
    quote_state: QuoteState = Field(..., description="見積もりの状態")

    created_at: datetime = Field(..., description="見積もり作成日時")
    updated_at: datetime = Field(..., description="見積もり更新日時")
    created_by: Optional[str] = Field(None, description="作成者（オペレータIDなど）")
    updated_by: Optional[str] = Field(None, description="更新者（オペレータIDなど）")

    # --- quote_detailsテーブル項目（契約条件） ---
    birth_date: date = Field(..., description="契約者の生年月日")
    gender: str = Field(..., description="性別（male / female / other）")
    monthly_premium: int = Field(..., description="月額保険料（円）")
    payment_period_years: int = Field(..., description="払込期間（年）")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無")
    pension_payment_years: int = Field(..., description="年金受取年数（年）")

    # --- quote_detailsテーブル項目（計算結果） ---
    contract_date: date = Field(..., description="契約開始日")
    contract_interest_rate: float = Field(..., description="契約時利率（%）")
    total_paid_amount: int = Field(..., description="総払込額（円）")
    pension_start_age: int = Field(..., description="年金受給開始年齢")
    annual_tax_deduction: int = Field(..., description="年間税控除額（円）")

    # --- 商品情報連携コード（任意） ---
    plan_code: Optional[str] = Field(None, description="商品コード（MongoDB商品情報と連携）")

    # --- MongoDBシナリオ情報 ---
    scenarios: List[PensionQuoteScenarioModel] = Field(..., description="利率シナリオ一覧")

    class Config:
        orm_mode = True  # SQLAlchemyモデルからの変換を許容

class QuoteStateUpdateModel(BaseModel):
    """
    ステータス変更結果を示すモデル
    - 更新対象の見積もりIDと、更新前・更新後の状態を保持
    """
    quote_id: str
    from_state: QuoteState = Field(..., description="変更前の見積もりステータス")
    to_state: QuoteState = Field(..., description="変更後の見積もりステータス")

class QuoteStateUpdateRequest(BaseModel):
    """
    見積もりステータス変更リクエストモデル
    - PUT時のBodyに指定
    """
    new_state: QuoteState

# ------------------------------------------------------------------------------
# 見積もり更新モデル
# ------------------------------------------------------------------------------
class PartialQuoteUpdateModel(PensionQuoteRequestModel):
    """
    見積もり情報の一部を更新するための入力モデル
    - 未指定のフィールドは変更されない（PATCHの性質に準拠）
    """
    birth_date: Optional[date] = Field(None, description="契約者の生年月日（例: 1990-01-01）")
    gender: Optional[Literal["male", "female"]] = Field(None, description="性別（male / female）")
    monthly_premium: Optional[conint(ge=10000, le=50000, multiple_of=1000)] = Field(None, description="月額保険料（¥10,000〜¥50,000、1,000円単位）")
    payment_period_years: Optional[conint(ge=15, le=45)] = Field(None, description="払込期間（15〜45年）")
    pension_payment_years: Optional[conint(ge=5, le=30)] = Field(None, description="年金受取期間（5〜30年）")
    tax_deduction_enabled: Optional[bool] = Field(None, description="税制適格特約の有無（True/False）")