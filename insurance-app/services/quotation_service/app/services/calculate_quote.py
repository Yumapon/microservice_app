# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりロジック

- 契約開始日の算出
- 控除額・受取金額のシミュレーション
- MongoDBから予定利率（標準・最低保証・高金利）を取得
- レスポンス用スキーマ（PensionQuoteResponseModel）を構築して返却

※ このモジュールは「見積もりの生成専用」であり、保存処理は行わない
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from datetime import date, datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, List

from motor.motor_asyncio import AsyncIOMotorClient

from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    PensionQuoteScenarioModel
)
from app.services.rate_loader import load_interest_rates

# ------------------------------------------------------------------------------
# ロガー初期化
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 契約開始日ロジック
# ------------------------------------------------------------------------------
def get_contract_start_date(today: date) -> date:
    """
    契約開始日を算出（毎月1日始まり、常に00:00）

    Parameters:
        today (date): 今日の日付

    Returns:
        date: 契約開始日（翌月1日 or 当月1日）
    """
    logger.debug("[契約日計算] 今日の日付: %s", today)
    if today.day == 1:
        return today
    next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    logger.debug("[契約日確定] 翌月1日を採用: %s", next_month)
    return next_month

# ------------------------------------------------------------------------------
# 金額・年金の計算ロジック
# ------------------------------------------------------------------------------
def calculate_benefits(monthly_premium: int, years: int, rate: float) -> Dict[str, float]:
    """
    将来受取金額や返戻金を計算

    Returns:
        dict: 累計・年金・一括受取・15年返戻額等
    """
    logger.debug("[給付計算] 月額=%d, 年数=%d, 利率=%.2f", monthly_premium, years, rate)
    total_paid = monthly_premium * 12 * years
    lump_sum = int(total_paid * (1 + rate) ** years)
    annual_pension = lump_sum // 10
    refund_at_15 = int(total_paid * (1 + rate) ** min(years, 15))
    refund_rate = round(refund_at_15 / (monthly_premium * 12 * 15) * 100, 2)

    return {
        "rate": rate,
        "total_paid": total_paid,
        "annual_pension": annual_pension,
        "lump_sum": lump_sum,
        "refund_at_15": refund_at_15,
        "refund_rate": refund_rate
    }

# ------------------------------------------------------------------------------
# シナリオ構築
# ------------------------------------------------------------------------------
def build_scenario(
    scenario_name: str,
    rate: float,
    monthly_premium: int,
    payment_years: int
) -> PensionQuoteScenarioModel:
    """
    利率シナリオを構築してモデル化

    Returns:
        PensionQuoteScenarioModel
    """
    logger.debug("[シナリオ構築] %s: rate=%.2f%%", scenario_name, rate)
    benefits = calculate_benefits(monthly_premium, payment_years, rate / 100)

    return PensionQuoteScenarioModel(
        scenario_name=scenario_name,
        assumed_interest_rate=rate,
        total_refund_amount=benefits["lump_sum"],
        annual_annuity=benefits["annual_pension"],
        lump_sum_amount=benefits["lump_sum"],
        refund_on_15_years=benefits["refund_at_15"],
        refund_rate_on_15_years=benefits["refund_rate"]
    )

# ------------------------------------------------------------------------------
# メイン処理：見積もり計算
# ------------------------------------------------------------------------------
async def calculate_quote(
    request: PensionQuoteRequestModel,
    mongo_client: AsyncIOMotorClient
) -> PensionQuoteResponseModel:
    """
    個人年金保険の見積もりシミュレーションを実行

    Parameters:
        request: ユーザー入力（Pydanticモデル）
        mongo_client: MongoDBクライアント

    Returns:
        PensionQuoteResponseModel
    """
    logger.info("[見積もり開始] 入力: %s", request.json())

    # 契約開始日（毎月1日始まり）
    today = date.today()
    contract_date = get_contract_start_date(today)

    # 利率情報をMongoDBから取得（標準、最低保証、高金利）
    rates = await load_interest_rates(mongo_client, contract_date)
    logger.info("[利率取得] contract=%.2f, min=%.2f, high=%.2f",
                rates["contract_rate"], rates["min_rate"], rates["high_rate"])

    # 支払総額・年金開始年齢
    total_paid_amount = request.monthly_premium * 12 * request.payment_period_years
    pension_start_age = contract_date.year - request.birth_date.year
    if contract_date < request.birth_date.replace(year=contract_date.year):
        pension_start_age -= 1

    annual_tax_deduction = 40000  # 現状は仮設定

    # 利率シナリオの構築
    scenarios: List[PensionQuoteScenarioModel] = [
        build_scenario("標準", rates["contract_rate"], request.monthly_premium, request.payment_period_years),
        build_scenario("最低保証", rates["min_rate"], request.monthly_premium, request.payment_period_years),
        build_scenario("高金利", rates["high_rate"], request.monthly_premium, request.payment_period_years)
    ]

    # レスポンスモデル構築（user_idは含めない）
    response = PensionQuoteResponseModel(
        quote_id=uuid4(),
        contract_date=contract_date,
        contract_interest_rate=rates["contract_rate"],
        total_paid_amount=total_paid_amount,
        payment_period_years=request.payment_period_years,
        pension_start_age=pension_start_age,
        annual_tax_deduction=annual_tax_deduction,
        scenarios=scenarios
    )

    logger.info("[見積もり完了] quote_id=%s", response.quote_id)
    return response
