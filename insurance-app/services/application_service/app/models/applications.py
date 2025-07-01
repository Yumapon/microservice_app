# -*- coding: utf-8 -*-
"""
保険契約申込に使用するモデル定義

- ApplicationRequestModel:
    フロントエンド/BFF → バックエンドに申込要求を送る際に使用。
- ApplicationResponseModel:
    バックエンド → フロントエンドに申込結果を返却する際に使用。
- PensionQuoteScenarioModel:
    年金保険のシナリオ別返戻結果を保持。
"""

from typing import List, Literal, Dict
from pydantic import BaseModel, Field
from datetime import date


# ------------------------------------------------------------------------------
# 年金保険の返戻シナリオモデル
# ------------------------------------------------------------------------------
class PensionQuoteScenarioModel(BaseModel):
    """
    想定利率ごとの返戻シナリオ

    - quotation_service 側の見積もりロジックで算出される。
    - 年金額・一括返戻金・中途解約返戻金などを含む。
    """
    scenario_name: str = Field(..., description="シナリオ名（例：標準、最低保証）")
    assumed_interest_rate: float = Field(..., description="このシナリオの想定利率（%）")
    total_refund_amount: int = Field(..., description="最終返戻総額（円）")
    annual_annuity: int = Field(..., description="毎年の年金額（円）")
    lump_sum_amount: int = Field(..., description="一括受取金額（円）")
    refund_on_15_years: int = Field(..., description="15年後の解約返戻金（円）")
    refund_rate_on_15_years: float = Field(..., description="15年後の返戻率（％）")


# ------------------------------------------------------------------------------
# 保険申込リクエストモデル（POST用）
# ------------------------------------------------------------------------------
class ApplicationRequestModel(BaseModel):
    """
    保険申込要求モデル

    - ユーザーがフロントエンド上で取得・確認した見積もり結果（スナップショット）を含む。
    - quotation_service で取得したデータをそのまま保持することで、
      backend で整合性チェック・DB登録を行う。
    """
    quote: Dict = Field(..., description="quotation_service から取得済みの見積もり情報（JSON構造のスナップショット）")


# ------------------------------------------------------------------------------
# 保険申込レスポンスモデル（GET/POSTレスポンス用）
# ------------------------------------------------------------------------------
class ApplicationResponseModel(BaseModel):
    """
    保険申込応答モデル

    - フロントエンドやBFFが申込完了後や申込状況照会時に使用。
    - 見積もり取得時点の契約条件・計算結果・利率をスナップショット形式で保持。
    """

    # 識別情報
    application_id: str = Field(..., description="申込ID（UUID）")
    quote_id: str = Field(..., description="申込元の見積もりID（UUID）")

    # ステータス
    status: Literal["none", "applied", "reverted", "cancelled"] = Field(
        ..., description="申込ステータス（none: 未処理, applied: 申請済, reverted: 差戻し, cancelled: キャンセル済）"
    )

    # 契約条件（ユーザー入力値）のスナップショット
    snapshot_birth_date: date = Field(..., description="契約者の生年月日")
    snapshot_gender: Literal["male", "female", "other"] = Field(..., description="契約者の性別")
    snapshot_monthly_premium: int = Field(..., description="月額保険料（円）")
    snapshot_payment_period_years: int = Field(..., description="保険料払込期間（年）")
    snapshot_tax_deduction_enabled: bool = Field(..., description="保険料控除対象か")

    # 見積もり結果のスナップショット（quotation_service 計算結果）
    snapshot_contract_date: date = Field(..., description="契約開始日（想定）")
    snapshot_contract_interest_rate: float = Field(..., description="契約時予定利率（％）")
    snapshot_total_paid_amount: int = Field(..., description="保険料総額（円）")
    snapshot_pension_start_age: int = Field(..., description="年金開始年齢")
    snapshot_annual_tax_deduction: int = Field(..., description="年間控除見込額（円）")

    # 想定利率別のシナリオ一覧
    scenario_data: List[PensionQuoteScenarioModel] = Field(..., description="利率ごとの返戻シナリオ情報")


# ------------------------------------------------------------------------------
# 保険申込レスポンスモデル（更新時）
# ------------------------------------------------------------------------------
class ApplicationStatusResponseModel(BaseModel):
    application_id: str
    quote_id: str
    status: str