# -*- coding: utf-8 -*-
"""
PostgreSQL用 quote_details テーブルのSQLAlchemyモデル定義

このテーブルは quotes テーブルと 1対1 の関係にあり、
見積もり時の契約条件および見積もり結果（スナップショット）を保持する。
MongoDB等の外部情報と連携する場合は plan_code を利用する。
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from sqlalchemy import Column, Date, Integer, Boolean, Numeric, ForeignKey, TIMESTAMP, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

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

    plan_code = Column(
        String,
        nullable=True,
        comment="商品コード（MongoDBのplan情報と連携するための識別子）"
    )

    birth_date = Column(Date, nullable=False, comment="契約者の生年月日")
    gender = Column(String, nullable=False, comment="性別（'男' または '女'）")
    monthly_premium = Column(Integer, nullable=False, comment="月額保険料（円）")
    payment_period_years = Column(Integer, nullable=False, comment="払込期間（年）")
    tax_deduction_enabled = Column(Boolean, nullable=False, comment="税制適格特約の有無（True/False）")

    contract_date = Column(Date, nullable=False, comment="契約開始日")
    contract_interest_rate = Column(Numeric(5, 2), nullable=False, comment="契約時利率（%）")
    total_paid_amount = Column(Integer, nullable=False, comment="総払込額（円）")
    pension_start_age = Column(Integer, nullable=False, comment="年金受給開始年齢")
    annual_tax_deduction = Column(Integer, nullable=False, comment="年間税控除額（円）")

    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="作成日時"
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=datetime.utcnow,
        comment="更新日時"
    )

    created_by = Column(String, nullable=True, comment="作成者（ユーザーIDまたはオペレータID）")
    updated_by = Column(String, nullable=True, comment="更新者（ユーザーIDまたはオペレータID）")
