# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりロジック（実務対応版）

- 契約条件バリデーション（契約年齢、払込年数）
- 控除額・受取金額の業務ルールに基づく計算
- MongoDBから利率を取得（例：標準・最低保証・高金利）
- シナリオ生成（3パターン）＋ 見積もり結果レスポンス生成
"""

import logging
from datetime import date, timedelta
from uuid import uuid4, UUID
from typing import Dict, List

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    PensionQuoteScenarioModel
)
from app.services.rate_loader import load_interest_rates
from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
rules = config.insurance
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 業務ルール定数
# ------------------------------------------------------------------------------
MIN_AGE = rules.get("min_age", 20)
MAX_AGE = rules.get("max_age", 70)
MIN_PAYMENT_YEARS = rules.get("min_payment_years", 15)
MAX_ANNUAL_TAX_DEDUCTION = rules.get("max_annual_tax_deduction", 40000)

# ------------------------------------------------------------------------------
# 契約開始日算出ロジック
# ------------------------------------------------------------------------------
def get_contract_start_date(today: date) -> date:
    """
    契約開始日を算出（毎月1日開始）

    Parameters:
        today (date): 今日の日付

    Returns:
        date: 契約日（毎月1日）
    """
    logger.debug("[契約日計算] 今日: %s", today)
    if today.day == 1:
        return today
    next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
    logger.debug("[契約日確定] 翌月1日: %s", next_month)
    return next_month

# ------------------------------------------------------------------------------
# 金額・給付シミュレーション
# ------------------------------------------------------------------------------
def calculate_benefits(monthly_premium: int, years: int, rate: float, pension_duration_years: int) -> Dict[str, float]:
    """
    将来受取金額や返戻金をシミュレート

    Returns:
        dict: 金額シミュレーション結果
    """
    total_paid = monthly_premium * 12 * years
    lump_sum = int(total_paid * (1 + rate) ** years)
    annual_pension = lump_sum // pension_duration_years
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
# シナリオ構築（各利率パターン）
# ------------------------------------------------------------------------------
def build_scenario(
    quote_id: UUID,
    scenario_type: str,
    rate: float,
    monthly_premium: int,
    payment_years: int
) -> PensionQuoteScenarioModel:
    """
    シナリオモデルを生成

    Returns:
        PensionQuoteScenarioModel
    """
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
# メイン処理：見積もり生成
# ------------------------------------------------------------------------------
async def calculate_quote(
    request: PensionQuoteRequestModel,
    mongo_client: AsyncIOMotorClient
) -> PensionQuoteResponseModel:
    """
    個人年金保険の見積もりを生成（MongoDBの予定利率を使用）

    Parameters:
        request: 入力リクエストモデル
        mongo_client: MongoDBクライアント

    Returns:
        PensionQuoteResponseModel
    """
    logger.info("[見積もり開始] 入力: %s", request.json())

    # ─────────────────────────────────────
    # Step 1: 契約開始日と年齢を算出
    # ─────────────────────────────────────
    today = date.today()
    contract_date = get_contract_start_date(today)
    birth_date = request.birth_date

    pension_start_age = contract_date.year - birth_date.year
    if contract_date < birth_date.replace(year=contract_date.year):
        pension_start_age -= 1

    logger.debug("[年金開始年齢] %d歳", pension_start_age)

    # 年齢制限チェック
    if pension_start_age < CONTRACT_MIN_AGE or pension_start_age > CONTRACT_MAX_AGE:
        logger.warning("[契約年齢エラー] %d歳", pension_start_age)
        raise HTTPException(status_code=400, detail=f"契約年齢は{CONTRACT_MIN_AGE}〜{CONTRACT_MAX_AGE}歳の範囲です")

    # 払込期間チェック
    if request.payment_period_years < MIN_PAYMENT_YEARS:
        raise HTTPException(status_code=400, detail=f"払込期間は最低{MIN_PAYMENT_YEARS}年以上必要です")

    # ─────────────────────────────────────
    # Step 2: MongoDBから利率情報を取得
    # ─────────────────────────────────────
    try:
        rates = await load_interest_rates(mongo_client, contract_date)
    except Exception as e:
        logger.exception("[利率取得失敗] MongoDBエラー")
        raise HTTPException(status_code=503, detail="利率情報の取得に失敗しました")

    logger.info("[利率取得] 標準=%.2f, 最低=%.2f, 高金利=%.2f",
                rates["contract_rate"], rates["min_rate"], rates["high_rate"])

    # 利率異常チェック（業務ルール上の上限などあればここで対応）

    # ─────────────────────────────────────
    # Step 3: 各シナリオの構築
    # ─────────────────────────────────────
    scenarios: List[PensionQuoteScenarioModel] = [
        build_scenario("標準", rates["contract_rate"], request.monthly_premium, request.payment_period_years),
        build_scenario("最低保証", rates["min_rate"], request.monthly_premium, request.payment_period_years),
        build_scenario("高金利", rates["high_rate"], request.monthly_premium, request.payment_period_years)
    ]

    # ─────────────────────────────────────
    # Step 4: レスポンス構築（保存は外部ロジックに委譲）
    # ─────────────────────────────────────
    total_paid_amount = request.monthly_premium * 12 * request.payment_period_years

    response = PensionQuoteResponseModel(
        quote_id=uuid4(),
        contract_date=contract_date,
        contract_interest_rate=rates["contract_rate"],
        total_paid_amount=total_paid_amount,
        payment_period_years=request.payment_period_years,
        pension_start_age=pension_start_age,
        annual_tax_deduction=MAX_ANNUAL_TAX_DEDUCTION,
        scenarios=scenarios
    )

    logger.info("[見積もり完了] quote_id=%s", response.quote_id)
    return response
