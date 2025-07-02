"""create quote tables

Revision ID: 20250702_create_quote_tables
Revises: 
Create Date: 2025-07-02

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '20250702_create_quote_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # quotes テーブル
    op.create_table(
        'quotes',
        sa.Column('quote_id', postgresql.UUID(as_uuid=True), primary_key=True, comment='見積もりID'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ユーザーID'),
        sa.Column('birth_date', sa.Date(), nullable=False, comment='契約者の生年月日'),
        sa.Column('gender', sa.String(), nullable=False, comment='性別'),
        sa.Column('monthly_premium', sa.Integer(), nullable=False, comment='月額保険料（円）'),
        sa.Column('payment_period_years', sa.Integer(), nullable=False, comment='払込期間（年）'),
        sa.Column('tax_deduction_enabled', sa.Boolean(), nullable=False, comment='税制適格特約の有無'),
        sa.Column('contract_date', sa.Date(), nullable=False, comment='契約開始日'),
        sa.Column('contract_interest_rate', sa.Numeric(5, 2), nullable=False, comment='契約時利率（%）'),
        sa.Column('total_paid_amount', sa.Integer(), nullable=False, comment='総払込額（円）'),
        sa.Column('pension_start_age', sa.Integer(), nullable=False, comment='年金受給開始年齢'),
        sa.Column('annual_tax_deduction', sa.Integer(), nullable=False, comment='年間税控除額（円）'),
        sa.Column('quote_state', sa.String(), nullable=False, server_default='none', comment='見積もり状態'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='作成日時'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新日時'),
        sa.Column('created_by', sa.String(), nullable=True, comment='作成者'),
        sa.Column('updated_by', sa.String(), nullable=True, comment='更新者'),
    )

    # quote_details テーブル
    op.create_table(
        'quote_details',
        sa.Column('quote_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quotes.quote_id', ondelete='CASCADE'), primary_key=True, comment='見積もりID'),
        sa.Column('plan_code', sa.String(), nullable=True, comment='商品コード'),
        sa.Column('birth_date', sa.Date(), nullable=False, comment='契約者の生年月日'),
        sa.Column('gender', sa.String(), nullable=False, comment='性別'),
        sa.Column('monthly_premium', sa.Integer(), nullable=False, comment='月額保険料'),
        sa.Column('payment_period_years', sa.Integer(), nullable=False, comment='払込期間'),
        sa.Column('tax_deduction_enabled', sa.Boolean(), nullable=False, comment='税制適格特約の有無'),
        sa.Column('contract_date', sa.Date(), nullable=False, comment='契約開始日'),
        sa.Column('contract_interest_rate', sa.Numeric(5, 2), nullable=False, comment='契約時利率'),
        sa.Column('total_paid_amount', sa.Integer(), nullable=False, comment='総払込額'),
        sa.Column('pension_start_age', sa.Integer(), nullable=False, comment='年金受給開始年齢'),
        sa.Column('annual_tax_deduction', sa.Integer(), nullable=False, comment='年間税控除額'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='作成日時'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新日時'),
        sa.Column('created_by', sa.String(), nullable=True, comment='作成者'),
        sa.Column('updated_by', sa.String(), nullable=True, comment='更新者'),
    )

    # quote_scenarios テーブル
    op.create_table(
        'quote_scenarios',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), comment='シナリオID'),
        sa.Column('quote_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quote_details.quote_id', ondelete='CASCADE'), nullable=False, comment='見積もりID'),
        sa.Column('scenario_name', sa.String(), nullable=False, comment='シナリオ名'),
        sa.Column('assumed_interest_rate', sa.Numeric(5, 2), nullable=False, comment='想定利率'),
        sa.Column('total_refund_amount', sa.Integer(), nullable=False, comment='累計返戻金額'),
        sa.Column('annual_annuity', sa.Integer(), nullable=False, comment='年金形式で受け取る年間金額'),
        sa.Column('lump_sum_amount', sa.Integer(), nullable=False, comment='一括受取金額'),
        sa.Column('refund_on_15_years', sa.Integer(), nullable=False, comment='15年払込時点の返戻金額'),
        sa.Column('refund_rate_on_15_years', sa.Numeric(5, 2), nullable=False, comment='15年払込時点の返戻率'),
    )


def downgrade():
    op.drop_table('quote_scenarios')
    op.drop_table('quote_details')
    op.drop_table('quotes')
