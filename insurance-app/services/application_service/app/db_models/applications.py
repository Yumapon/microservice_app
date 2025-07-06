# -*- coding: utf-8 -*-
"""
PostgreSQL用 applications テーブルおよび application_details テーブルのSQLAlchemyモデル定義
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from sqlalchemy import Column, String, Date, Integer, Boolean, Numeric, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime
import uuid

Base = declarative_base(cls=AsyncAttrs)

# ------------------------------------------------------------------------------
# Application モデル（申込情報）
# ------------------------------------------------------------------------------
class Application(Base):
    """
    applications テーブル
    - 見積もりに基づく保険申込情報を保持
    """
    __tablename__ = "applications"

    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="申込ID（UUID）")
    quote_id = Column(UUID(as_uuid=True), nullable=False, comment="対象見積もりID（quotes）")
    user_id = Column(UUID(as_uuid=True), nullable=False, comment="ユーザーID（Keycloakのsub）")

    application_status = Column(
        String(32),
        nullable=False,
        default="pending",
        server_default="pending",
        comment="申込ステータス（pending, under_review, confirmed, rejected, cancelled）"
    )

    approved_by = Column(UUID(as_uuid=True), nullable=True, comment="申込承認者ID（社内ユーザーID）")
    approval_date = Column(TIMESTAMP(timezone=True), nullable=False, comment="申込承認日時")
    application_number = Column(String, nullable=True, comment="社内管理用の申込番号")

    applied_at = Column(TIMESTAMP(timezone=True), nullable=False, comment="申込日時")
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"), onupdate=datetime.utcnow, comment="更新日時")

    created_by = Column(String(64), nullable=True, comment="作成者（オペレーターIDなど）")
    updated_by = Column(String(64), nullable=True, comment="更新者（オペレーターIDなど）")


# ------------------------------------------------------------------------------
# ApplicationDetail モデル（申込詳細：契約条件および計算結果）
# ------------------------------------------------------------------------------
class ApplicationDetail(Base):
    """
    application_details テーブル
    - 申込時の契約条件および見積もり計算結果をスナップショットとして保持
    - applications テーブルと 1対1 の関係
    """
    __tablename__ = "application_details"

    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("applications.application_id", ondelete="CASCADE"),
        primary_key=True,
        comment="申込ID（applicationsと1対1）"
    )

    # 契約条件
    birth_date = Column(Date, nullable=False, comment="契約者の生年月日")
    gender = Column(String, nullable=False, comment="性別（'male', 'female', 'other'）")
    monthly_premium = Column(Integer, nullable=False, comment="月額保険料（円）")
    payment_period_years = Column(Integer, nullable=False, comment="払込期間（年）")
    tax_deduction_enabled = Column(Boolean, nullable=False, comment="税制適格特約の有無（True/False）")

    # 計算結果
    contract_date = Column(Date, nullable=False, comment="契約開始日")
    contract_interest_rate = Column(Numeric(5, 2), nullable=False, comment="契約時利率（%）")
    total_paid_amount = Column(Integer, nullable=False, comment="総払込額（円）")
    pension_start_age = Column(Integer, nullable=False, comment="年金受給開始年齢")
    annual_tax_deduction = Column(Integer, nullable=False, comment="年間税控除額（円）")

    # 商品連携用コード
    plan_code = Column(String, nullable=False, comment="商品コード（MongoDB商品情報と連携）")

    # 支払い方法など、申し込み時の追加カラム
    user_consent = Column(Boolean, nullable=False, comment="同意の有無（重要事項説明への同意）")
    payment_method = Column(String(32), nullable=False, comment="支払方法（クレカ・口座振替など）")
    identity_verified = Column(Boolean, nullable=False, comment="本人確認完了フラグ")