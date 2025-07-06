# -*- coding: utf-8 -*-
"""
保険申込に関するAPIスキーマ定義（リクエスト・レスポンス・状態列挙など）
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from datetime import date, datetime
from uuid import UUID
from typing import Optional, Literal, List
from enum import Enum

from pydantic import BaseModel, Field, PrivateAttr

# ------------------------------------------------------------------------------
# 申込ステータス列挙型
# ------------------------------------------------------------------------------
class ApplicationState(str, Enum):
    """
    申込の状態を示す列挙型
    """
    pending = "pending"
    under_review = "under_review"
    confirmed = "confirmed"
    rejected = "rejected"
    cancelled = "cancelled"

# ------------------------------------------------------------------------------
# 保険金代理受取人（MongoDB用）
# ------------------------------------------------------------------------------
class ApplicationBeneficiaryItem(BaseModel):
    name: str
    relation: str
    allocation: int
    note: str

class ApplicationBeneficiariesModel(BaseModel):
    """
    MongoDBに保存される申込者の受取人情報モデル
    - application_id: 紐づく申込ID
    - beneficiaries: 任意の構造を許容する受取人情報（JSON）
    - updated_at: 最終更新日時
    """
    application_id: UUID = Field(..., description="申込ID")
    beneficiaries: List[ApplicationBeneficiaryItem] = Field(..., description="受取人情報（任意のJSON構造）")
    updated_at: datetime = Field(..., description="最終更新日時（ISO形式）")

# ------------------------------------------------------------------------------
# 保険金代理受取人（API受け取り用）
# ------------------------------------------------------------------------------
class ApplicationBeneficiaryRequestModel(BaseModel):
    name: str = Field(..., description="受取人氏名")
    relation: str = Field(..., description="契約者との関係（例: 子、配偶者）")
    allocation: int = Field(..., description="受取割合（%）")
    note: Optional[str] = Field(None, description="備考")

# ------------------------------------------------------------------------------
# 見積もりサービスから取得した見積もり情報を格納する型
# ------------------------------------------------------------------------------
class QuoteScenarioModel(BaseModel):
    """
    MongoDBに保存された見積もりシナリオ情報
    """
    quote_id: UUID = Field(..., description="見積もりID")
    scenario_type: str = Field(..., description="シナリオタイプ（例：base, low, high）")
    interest_rate: float = Field(..., description="想定利率（％）")
    estimated_pension: int = Field(..., description="毎月の想定年金額（円）")
    pension_refund_rate: float = Field(..., description="年金受取総額の返戻率")
    annual_pension: int = Field(..., description="年金年額（円）")
    lump_sum_amount: int = Field(..., description="一括受取金額（円）")
    lump_sum_refund_rate: float = Field(..., description="一括受取時の返戻率（％）")
    refund_on_15_years: int = Field(..., description="15年後の返戻金（使わない場合は0）")
    refund_rate: float = Field(..., description="返戻率（使わない場合は0）")
    note: Optional[str] = Field(None, description="備考")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

class QuoteSummaryModel(BaseModel):
    """
    application_service 内部で利用する、quotation_service から取得した見積もり要約モデル
    """
    quote_id: UUID = Field(..., description="見積もりID")
    user_id: UUID = Field(..., description="ユーザーID")
    birth_date: date = Field(..., description="契約者の生年月日")
    gender: str = Field(..., description="性別（male / female）")
    monthly_premium: int = Field(..., description="月額保険料（円）")
    payment_period_years: int = Field(..., description="支払年数")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無（True/False）")
    contract_date: date = Field(..., description="契約開始日")
    contract_interest_rate: float = Field(..., description="契約利率（％）")
    total_paid_amount: int = Field(..., description="総払込額（円）")
    pension_start_age: int = Field(..., description="年金受給開始年齢")
    annual_tax_deduction: int = Field(..., description="年間税控除額（円）")
    quote_state: Optional[str] = Field(None, description="見積もり状態")
    created_at: Optional[datetime] = Field(None, description="見積もり作成日時")
    updated_at: Optional[datetime] = Field(None, description="見積もり更新日時")
    plan_code: Optional[str] = Field(None, description="商品コード")

    scenarios: List[QuoteScenarioModel] = Field(..., description="利率別シナリオ情報")

# ------------------------------------------------------------------------------
# 利率シナリオモデル（MongoDBへ格納するデータ）
# ------------------------------------------------------------------------------
class PensionApplicationScenarioModel(BaseModel):
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
# Application作成リクエストモデル（POST用）
# ------------------------------------------------------------------------------
class PensionApplicationRequestModel(BaseModel):
    """
    保険申込作成時のリクエストモデル
    """
    quote_id: UUID = Field(..., description="見積もりID")
    user_consent: bool = Field(..., description="重要事項説明への同意有無（True/False）")
    payment_method: str = Field(..., description="支払方法（例: credit_card, bank_transfer）")
    identity_verified: bool = Field(..., description="本人確認完了フラグ（True/False）")
    beneficiaries: List[ApplicationBeneficiaryRequestModel] = Field(..., description="保険金受け取り代理人")

# ------------------------------------------------------------------------------
# Applicationレスポンスモデル（application + application_details 統合）
# ------------------------------------------------------------------------------
class PensionApplicationResponseModel(BaseModel):
    """
    保険申込のレスポンスモデル（application + detail）
    """
    # --- applications テーブル情報 ---
    application_id: UUID = Field(..., description="申込ID（UUID）")
    quote_id: UUID = Field(..., description="見積もりID（UUID）")
    user_id: UUID = Field(..., description="ユーザーID（UUID）")
    application_status: ApplicationState = Field(..., description="申込ステータス")

    user_consent: bool = Field(..., description="同意有無")
    payment_method: str = Field(..., description="支払方法（申込時）")
    identity_verified: bool = Field(..., description="本人確認完了フラグ")

    approved_by: Optional[UUID] = Field(None, description="申込承認者ID（オペレーター）")
    approval_date: Optional[datetime] = Field(None, description="申込承認日時")
    application_number: Optional[str] = Field(None, description="社内管理用の申込番号")

    applied_at: datetime = Field(..., description="申込日時")
    updated_at: Optional[datetime] = Field(None, description="申込更新日時")
    created_by: Optional[str] = Field(None, description="作成者（オペレーターID）")
    updated_by: Optional[str] = Field(None, description="更新者（オペレーターID）")

    # --- application_details テーブル情報 ---
    birth_date: date = Field(..., description="契約者の生年月日")
    gender: Literal["male", "female", "other"] = Field(..., description="性別")
    monthly_premium: int = Field(..., description="月額保険料（円）")
    payment_period_years: int = Field(..., description="払込期間（年）")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無")

    contract_date: date = Field(..., description="契約開始日")
    contract_interest_rate: float = Field(..., description="契約利率（%）")
    total_paid_amount: int = Field(..., description="総支払額（円）")
    pension_start_age: int = Field(..., description="年金開始年齢")
    annual_tax_deduction: int = Field(..., description="年間控除額（円）")

    plan_code: str = Field(..., description="商品コード（スナップショット）")
    detail_payment_method: str = Field(..., description="支払方法（詳細スナップショット）")

    # --- MongoDBシナリオ情報 ---
    scenarios: List[PensionApplicationScenarioModel] = Field(..., description="利率シナリオ一覧")

    # --- MongoDB保険金代理受取人情報 ---
    beneficiaries: List[ApplicationBeneficiariesModel] = Field(..., description="保険金代理受取人一覧")

    class Config:
        orm_mode = True

# ------------------------------------------------------------------------------
# Application更新モデル
# ------------------------------------------------------------------------------
class PartialApplicationUpdateModel(PensionApplicationRequestModel):
    """
    申し込み情報の一部を更新するための入力モデル
    - 未指定のフィールドは変更されない（PATCHの性質に準拠）
    """
    quote_id: Optional[UUID] = Field(None, description="見積もりID ※変更不可。")
    user_consent: Optional[bool] = Field(None, description="重要事項説明への同意有無（True/False）")
    payment_method: Optional[str] = Field(None, description="支払方法（例: credit_card, bank_transfer）")
    identity_verified: Optional[bool] = Field(None, description="本人確認完了フラグ（True/False）")
    beneficiaries: Optional[List[ApplicationBeneficiaryRequestModel]] = Field(None, description="保険金受け取り代理人")

# ------------------------------------------------------------------------------
# Applicationステータス更新レスポンスモデル
# ------------------------------------------------------------------------------
class ApplicationStatusUpdateModel(BaseModel):
    """
    ステータス変更結果を示すモデル
    - 更新対象の申込IDと、更新前・更新後の状態を保持
    """
    application_id: str = Field(..., description="申込ID")
    from_status: ApplicationState = Field(..., description="変更前の申込ステータス")
    to_status: ApplicationState = Field(..., description="変更後の申込ステータス")

class ApplicationStatusUpdateRequest(BaseModel):
    """
    見積もりステータス変更リクエストモデル
    - PUT時のBodyに指定
    """
    new_state: ApplicationState = Field(..., description="変更後の申込ステータス")

# ------------------------------------------------------------------------------
# 保険計算の結果を返却するモデル
# ------------------------------------------------------------------------------
class PensionApplicationCalculateResult(BaseModel):
    quote_id: UUID
    contract_date: date
    contract_interest_rate: float
    total_paid_amount: int
    pension_start_age: int
    annual_tax_deduction: int
    scenarios: List[PensionApplicationScenarioModel]