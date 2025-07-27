from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, date


class ContractResponseModel(BaseModel):
    """
    契約情報のレスポンスモデル
    - contracts テーブルに対応
    """

    contract_id: UUID = Field(..., description="契約ID（UUID）")
    application_id: UUID = Field(..., description="申込ID（applications）")
    quote_id: UUID = Field(..., description="見積もりID（quotes）")
    user_id: UUID = Field(..., description="契約者のユーザーID")

    # 契約時のユーザー入力情報（スナップショット）
    gender: str = Field(..., description="契約者の性別")
    birth_date: date = Field(..., description="契約者の生年月日")
    monthly_premium: int = Field(..., description="月額保険料")
    payment_period_years: int = Field(..., description="払込年数")
    pension_payment_years: int = Field(..., description="年金受取年数")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約の有無")

    # 契約条件と結果のスナップショット
    contract_date: date = Field(..., description="契約開始日")
    contract_interest_rate: float = Field(..., description="契約利率")
    total_amount_paid: int = Field(..., description="総払込保険料")
    total_amount_returned: int = Field(..., description="総受取金額")
    refund_rate: float = Field(..., description="返戻率（%）")
    tax_deduction_amount: Optional[int] = Field(None, description="税控除見込額（適用時）")

    # JSONB形式で保存される詳細シナリオ情報
    scenario_data: Dict[str, Any] = Field(..., description="試算時のシナリオ情報（複数シナリオ）")

    # 契約者の同意情報など
    user_consent: bool = Field(..., description="利用規約への同意")
    applied_at: datetime = Field(..., description="申込日時")

    # 作成・更新メタデータ
    created_at: datetime = Field(..., description="契約作成日時")
    updated_at: datetime = Field(..., description="契約更新日時")
    created_by: Optional[str] = Field(None, description="作成者ID（オペレータなど）")
    updated_by: Optional[str] = Field(None, description="更新者ID")

class ContractCreateModel(BaseModel):
    """
    契約作成リクエストモデル（内部処理用）
    - ApplicationStatusChangedEvent によってトリガーされる
    - application_id に紐づく情報を集約し、DB登録用に整形する
    """

    contract_id: UUID = Field(..., description="契約ID（UUID）")
    application_id: UUID = Field(..., description="申込ID")
    quote_id: UUID = Field(..., description="見積もりID")
    user_id: UUID = Field(..., description="契約者ユーザーID")

    # ユーザー入力・見積もりスナップショット
    gender: str = Field(..., description="性別")
    birth_date: date = Field(..., description="生年月日")
    monthly_premium: int = Field(..., description="月額保険料")
    payment_period_years: int = Field(..., description="払込年数")
    pension_payment_years: int = Field(..., description="年金受取年数")
    tax_deduction_enabled: bool = Field(..., description="税制適格特約")

    contract_date: date = Field(..., description="契約開始日")
    contract_interest_rate: float = Field(..., description="契約利率")
    total_amount_paid: int = Field(..., description="総払込保険料")
    total_amount_returned: int = Field(..., description="総受取額")
    refund_rate: float = Field(..., description="返戻率（%）")
    tax_deduction_amount: Optional[int] = Field(None, description="税控除見込額")

    # MongoDBから取得したシナリオ情報
    scenario_data: Dict[str, Any] = Field(..., description="シナリオ詳細データ")

    # 同意とタイムスタンプ
    user_consent: bool = Field(..., description="同意情報")
    applied_at: datetime = Field(..., description="申込日時")

    # メタ情報
    created_by: Optional[str] = Field(None, description="作成者（オペレータIDなど）")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="契約作成日時")

# ------------------------------------------------------------------------------
# 保険金代理受取人（MongoDB用）
# ------------------------------------------------------------------------------
class ContractBeneficiaryItem(BaseModel):
    name: str = Field(..., description="受取人氏名")
    relation: str = Field(..., description="契約者との関係（例: 子、配偶者）")
    allocation: int = Field(..., description="受取割合（%）")
    note: str = Field(..., description="備考欄")

class ContractBeneficiariesModel(BaseModel):
    """
    MongoDBに保存される契約者の受取人情報モデル
    - contract_id: 紐づく契約ID
    - beneficiaries: 複数の受取人情報（構造は申込と共通）
    - updated_at: 最終更新日時
    """
    contract_id: UUID = Field(..., description="契約ID")
    beneficiaries: List[ContractBeneficiaryItem] = Field(..., description="受取人情報リスト")
    updated_at: datetime = Field(..., description="最終更新日時（ISO形式）")