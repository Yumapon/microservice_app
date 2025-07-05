# -*- coding: utf-8 -*-
"""
PostgreSQL用 quotes テーブルのSQLAlchemyモデル定義
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from sqlalchemy import Column, String, Date, Integer, Boolean, Numeric, TIMESTAMP, text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
import uuid

Base = declarative_base(cls=AsyncAttrs)

# ------------------------------------------------------------------------------
# Quotes テーブル定義
# ------------------------------------------------------------------------------
class Quote(Base):
    """
    見積もり情報テーブル（quotes）
    """
    __tablename__ = "quotes"

    quote_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="見積もりID（UUID）")
    user_id = Column(UUID(as_uuid=True), nullable=False, comment="ユーザーID（UUID）")
    quote_state = Column(String, nullable=False, default="none", comment="見積もり状態（none, applied など）")

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), comment="見積もり作成日時")
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow, comment="見積もり更新日時")

    created_by = Column(String, nullable=True, comment="作成者（オペレータIDなど）")
    updated_by = Column(String, nullable=True, comment="更新者（オペレータIDなど）")

# ------------------------------------------------------------------------------
# QuoteDetail モデル（見積もり詳細）
# ------------------------------------------------------------------------------
class QuoteDetail(Base):
    """
    quote_details テーブル
    - 見積もりの契約条件および計算結果のスナップショットを保持
    - 1つの quote_id に対して1レコードのみ存在（1対1）
    """
    __tablename__ = "quote_details"

    quote_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quotes.quote_id", ondelete="CASCADE"),
        primary_key=True,
        comment="見積もりID（quotesと1対1）"
    )

    # 契約条件
    birth_date = Column(Date, nullable=False, comment="契約者の生年月日")
    gender = Column(
        String,
        nullable=False,
        comment="性別（'male', 'female', 'other'）"
    )
    monthly_premium = Column(Integer, nullable=False, comment="月額保険料（円）")
    payment_period_years = Column(Integer, nullable=False, comment="払込期間（年）")
    tax_deduction_enabled = Column(Boolean, nullable=False, comment="税制適格特約の有無（True/False）")
    pension_payment_years = Column(Integer, nullable=False, server_default="10", comment="年金受取年数（年）")

    # 計算結果
    contract_date = Column(Date, nullable=False, comment="契約開始日")
    contract_interest_rate = Column(Numeric(5, 2), nullable=False, comment="契約時利率（%）")
    total_paid_amount = Column(Integer, nullable=False, comment="総払込額（円）")
    pension_start_age = Column(Integer, nullable=False, comment="年金受給開始年齢")
    annual_tax_deduction = Column(Integer, nullable=False, comment="年間税控除額（円）")

    # 商品連携用コード
    plan_code = Column(String, nullable=True, comment="商品コード（MongoDB商品情報と連携）")
