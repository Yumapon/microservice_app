# -*- coding: utf-8 -*-
"""
PostgreSQL用 quote_scenarios テーブルのSQLAlchemyモデル定義

このテーブルは quote_details テーブルと 1対多 の関係を持ち、
想定利率ごとの見積もりシナリオ情報を行単位で保持する。
最低保証・標準・高金利など複数パターンの返戻額等をここに格納する。
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import FetchedValue

Base = declarative_base()

# ------------------------------------------------------------------------------
# QuoteScenario モデル（利率シナリオ）
# ------------------------------------------------------------------------------
class QuoteScenario(Base):
    """
    quote_scenarios テーブル
    - 見積もりの利率シナリオごとの結果（複数行）
    - quote_id は quote_details.quote_id を参照
    """
    __tablename__ = "quote_scenarios"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=FetchedValue(),  # DB側で gen_random_uuid() などが設定されていることを想定
        comment="シナリオID（UUID、主キー）"
    )

    quote_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_details.quote_id", ondelete="CASCADE"),
        nullable=False,
        comment="見積もりID（quote_detailsテーブルの外部キー）"
    )

    scenario_name = Column(String, nullable=False, comment="シナリオ名（例：標準、最低保証、高金利）")
    assumed_interest_rate = Column(Numeric(5, 2), nullable=False, comment="想定利率（%）")
    total_refund_amount = Column(Integer, nullable=False, comment="累計返戻金額（円）")
    annual_annuity = Column(Integer, nullable=False, comment="年金形式で受け取る年間金額（円）")
    lump_sum_amount = Column(Integer, nullable=False, comment="一括受取金額（円）")
    refund_on_15_years = Column(Integer, nullable=False, comment="15年間払込んだ場合の返戻金額（円）")
    refund_rate_on_15_years = Column(Numeric(5, 2), nullable=False, comment="15年間払込時点の返戻率（%）")
