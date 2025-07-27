from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Contract(Base):
    """
    contracts テーブル
    - 保険契約情報を管理する主テーブル
    """

    __tablename__ = "contracts"

    contract_id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="契約ID（UUID）")
    application_id = Column(PG_UUID(as_uuid=True), ForeignKey("applications.application_id"), nullable=False, comment="申込ID（applications）")
    quote_id = Column(PG_UUID(as_uuid=True), ForeignKey("quotes.quote_id"), nullable=False, comment="見積もりID（quotes）")
    user_id = Column(PG_UUID(as_uuid=True), nullable=False, comment="契約者のユーザーID")

    # --- 契約条件（スナップショット） ---
    gender = Column(String, nullable=False, comment="契約者の性別")
    birth_date = Column(Date, nullable=False, comment="契約者の生年月日")
    monthly_premium = Column(Integer, nullable=False, comment="月額保険料")
    payment_period_years = Column(Integer, nullable=False, comment="払込年数")
    pension_payment_years = Column(Integer, nullable=False, default=10, comment="年金受取年数")
    tax_deduction_enabled = Column(Boolean, nullable=False, comment="税制適格特約の有無")

    # --- 契約結果情報 ---
    contract_date = Column(Date, nullable=False, comment="契約開始日")
    contract_interest_rate = Column(Float, nullable=False, comment="契約利率")
    total_amount_paid = Column(Integer, nullable=False, comment="総払込保険料")
    total_amount_returned = Column(Integer, nullable=False, comment="総受取金額")
    refund_rate = Column(Float, nullable=False, comment="返戻率（%）")
    tax_deduction_amount = Column(Integer, nullable=True, comment="税控除見込額（適用時）")

    # --- 同意・申込情報 ---
    user_consent = Column(Boolean, nullable=False, comment="利用規約への同意")
    applied_at = Column(DateTime(timezone=True), nullable=False, comment="申込日時")

    # --- メタ情報 ---
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, comment="契約作成日時")
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="契約更新日時")
    created_by = Column(String, nullable=True, comment="作成者ID（オペレータなど）")
    updated_by = Column(String, nullable=True, comment="更新者ID")