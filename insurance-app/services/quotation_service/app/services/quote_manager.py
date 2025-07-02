# -*- coding: utf-8 -*-
"""
quotes, quote_details, quote_scenarios テーブルと連携するサービス層モジュール

- 見積もりの取得（一覧・個別）
- 見積もりの保存
- ステータス更新
"""

import logging
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.db.database import get_async_session
from app.db_models.quotes import Quote
from app.db_models.quote_details import QuoteDetail
from app.db_models.quote_scenarios import QuoteScenario
from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    PensionQuoteScenarioModel,
)

logger = logging.getLogger(__name__)

####参照処理

# ------------------------------------------------------------------------------
# 見積もり一覧取得（ユーザー単位）
# ------------------------------------------------------------------------------
async def get_quotes_by_user_id(session: AsyncSession, user_id: UUID) -> List[PensionQuoteResponseModel]:
    """
    指定ユーザーの見積もりを最新順で取得

    Returns:
        List[PensionQuoteResponseModel]
    """
    logger.info("見積もり一覧取得: user_id=%s", user_id)

    # quotes + quote_details JOIN
    stmt = (
        select(Quote, QuoteDetail)
        .join(QuoteDetail, Quote.quote_id == QuoteDetail.quote_id)
        .where(Quote.user_id == user_id)
        .order_by(Quote.created_at.desc())
    )
    results = await session.execute(stmt)
    records = results.all()

    quote_ids = [r.Quote.quote_id for r in records]
    scenarios_map = await _load_scenarios_map(session, quote_ids)

    responses = []
    for quote, detail in records:
        scenario_models = scenarios_map.get(quote.quote_id, [])
        responses.append(_build_response_model(quote, detail, scenario_models))

    return responses


# ------------------------------------------------------------------------------
# 見積もり単体取得
# ------------------------------------------------------------------------------
async def get_quote_by_id(session: AsyncSession, quote_id: UUID) -> PensionQuoteResponseModel:
    """
    見積もりIDを指定して1件取得
    """
    logger.info("見積もり取得: quote_id=%s", quote_id)

    result = await session.execute(
        select(Quote, QuoteDetail)
        .join(QuoteDetail)
        .where(Quote.quote_id == quote_id)
    )
    record = result.first()
    if not record:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")

    quote, detail = record
    scenarios = await _load_scenarios_by_quote_id(session, quote_id)
    return _build_response_model(quote, detail, scenarios)

####更新処理

# ------------------------------------------------------------------------------
# 見積もり保存処理（新規登録）
# ------------------------------------------------------------------------------
async def save_quote(
    session: AsyncSession,
    user_id: UUID,
    request: PensionQuoteRequestModel,
    response: PensionQuoteResponseModel,
    plan_code: str = None,
    operator_id: str = None
):
    """
    見積もりを3テーブル（quotes, quote_details, quote_scenarios）に保存

    Parameters:
        session (AsyncSession): 非同期DBセッション
        user_id (UUID): ユーザーID
        request (PensionQuoteRequestModel): 入力内容
        response (PensionQuoteResponseModel): 計算結果
    """
    logger.info("見積もり保存開始: quote_id=%s", response.quote_id)

    quote = Quote(
        quote_id=response.quote_id,
        user_id=user_id,
        quote_state="none",
        created_by=operator_id,
        updated_by=operator_id,
    )

    detail = QuoteDetail(
        quote_id=response.quote_id,
        plan_code=plan_code,
        birth_date=request.birth_date,
        gender=request.gender,
        monthly_premium=request.monthly_premium,
        payment_period_years=request.payment_period_years,
        tax_deduction_enabled=request.tax_deduction_enabled,
        contract_date=response.contract_date,
        contract_interest_rate=response.contract_interest_rate,
        total_paid_amount=response.total_paid_amount,
        pension_start_age=response.pension_start_age,
        annual_tax_deduction=response.annual_tax_deduction,
        created_by=operator_id,
        updated_by=operator_id,
    )

    scenarios = [
        QuoteScenario(
            quote_id=response.quote_id,
            scenario_name=s.scenario_name,
            assumed_interest_rate=s.assumed_interest_rate,
            total_refund_amount=s.total_refund_amount,
            annual_annuity=s.annual_annuity,
            lump_sum_amount=s.lump_sum_amount,
            refund_on_15_years=s.refund_on_15_years,
            refund_rate_on_15_years=s.refund_rate_on_15_years
        )
        for s in response.scenarios
    ]

    session.add_all([quote, detail, *scenarios])

    #Commit
    await session.commit()
    logger.info("見積もり保存完了")

# ------------------------------------------------------------------------------
# ステータス更新処理
# ------------------------------------------------------------------------------
async def mark_quote_state(session: AsyncSession, quote_id: UUID, user_id: UUID, new_state: str) -> PensionQuoteResponseModel:
    """
    見積もりステータスを更新
    """
    logger.info("ステータス更新: quote_id=%s, new_state=%s", quote_id, new_state)

    result = await session.execute(
        select(Quote).where(Quote.quote_id == quote_id)
    )
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")
    if quote.user_id != user_id:
        raise HTTPException(status_code=403, detail="他人の見積もりは更新できません")

    quote.quote_state = new_state

    #Commit
    await session.commit()

    return await get_quote_by_id(session, quote_id)

# ------------------------------------------------------------------------------
# 任意フィールド更新処理
# ------------------------------------------------------------------------------
async def update_quote(
    session: AsyncSession,
    quote_id: UUID,
    user_id: UUID,
    updates: dict
) -> PensionQuoteResponseModel:
    """
    見積もりの詳細情報（quote_details）を更新する

    Parameters:
        updates: 更新対象のフィールド辞書（バリデーション済を想定）
    """
    logger.info("見積もり更新開始: quote_id=%s", quote_id)

    result = await session.execute(
        select(Quote, QuoteDetail)
        .join(QuoteDetail)
        .where(Quote.quote_id == quote_id)
    )
    record = result.first()
    if not record:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")

    quote, detail = record
    if quote.user_id != user_id:
        raise HTTPException(status_code=403, detail="他人の見積もりは更新できません")

    for k, v in updates.items():
        if hasattr(detail, k):
            setattr(detail, k, v)

    #Commit
    await session.commit()
    scenarios = await _load_scenarios_by_quote_id(session, quote_id)
    return _build_response_model(quote, detail, scenarios)

# ------------------------------------------------------------------------------
# 見積もり削除
# ------------------------------------------------------------------------------

async def delete_quote(session: AsyncSession, quote_id: UUID, user_id: UUID):
    """
    見積もりを削除（子テーブルも CASCADE により削除）

    Raises:
        404: 存在しないquote_id
        403: 他ユーザーによる削除
    """
    logger.info("見積もり削除: quote_id=%s", quote_id)

    result = await session.execute(
        select(Quote).where(Quote.quote_id == quote_id)
    )
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")
    if quote.user_id != user_id:
        raise HTTPException(status_code=403, detail="他人の見積もりは削除できません")

    #データ削除
    await session.delete(quote)
    #Commit
    await session.commit()
    logger.info("見積もり削除完了: quote_id=%s", quote_id)


# ------------------------------------------------------------------------------
# 内部: シナリオ取得（複数）
# ------------------------------------------------------------------------------
async def _load_scenarios_map(session: AsyncSession, quote_ids: List[UUID]) -> dict:
    result = await session.execute(
        select(QuoteScenario).where(QuoteScenario.quote_id.in_(quote_ids))
    )
    scenarios = result.scalars().all()

    scenario_map = {}
    for s in scenarios:
        scenario_model = PensionQuoteScenarioModel.from_orm(s)
        scenario_map.setdefault(s.quote_id, []).append(scenario_model)
    return scenario_map


# ------------------------------------------------------------------------------
# 内部: シナリオ取得（単体）
# ------------------------------------------------------------------------------
async def _load_scenarios_by_quote_id(session: AsyncSession, quote_id: UUID) -> List[PensionQuoteScenarioModel]:
    result = await session.execute(
        select(QuoteScenario).where(QuoteScenario.quote_id == quote_id)
    )
    return [PensionQuoteScenarioModel.from_orm(s) for s in result.scalars().all()]


# ------------------------------------------------------------------------------
# 内部: レスポンスモデル組み立て
# ------------------------------------------------------------------------------
def _build_response_model(
    quote: Quote,
    detail: QuoteDetail,
    scenarios: List[PensionQuoteScenarioModel]
) -> PensionQuoteResponseModel:
    return PensionQuoteResponseModel(
        quote_id=quote.quote_id,
        contract_date=detail.contract_date,
        contract_interest_rate=detail.contract_interest_rate,
        total_paid_amount=detail.total_paid_amount,
        payment_period_years=detail.payment_period_years,
        pension_start_age=detail.pension_start_age,
        annual_tax_deduction=detail.annual_tax_deduction,
        scenarios=scenarios,
    )
