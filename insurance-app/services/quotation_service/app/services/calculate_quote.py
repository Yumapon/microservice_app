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
from typing import Dict, List, Optional

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteScenarioModel,
    PensionQuoteCalculateResult
)
from app.services.rate_loader import load_interest_rates
from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
rules = config.pension
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 業務ルール定数
# ------------------------------------------------------------------------------
MIN_AGE = rules.get("min_age", 20)
MAX_AGE = rules.get("max_age", 70)
MIN_PAYMENT_YEARS = rules.get("min_payment_years", 15)
MAX_ANNUAL_TAX_DEDUCTION = rules.get("max_annual_tax_deduction", 40000)
PLAN_CODE = rules.get("plan_code", "PENSION_001")

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
# 金額・給付シミュレーションロジック
# ------------------------------------------------------------------------------
def calculate_benefits(
    monthly_premium: int,
    payment_years: int,
    pension_years: int,
    contract_rate: float,
    annuity_conversion_rate: float,
    surrender_rates: Dict[int, float]
) -> Dict[str, float]:
    """
    利率ごとに金額・給付シミュレーションを行う（実務対応版）

    Parameters:
        monthly_premium: 月額保険料
        payment_years: 払込年数
        pension_years: 年金受取年数
        contract_rate: 積立期間中の予定利率（%）
        annuity_conversion_rate: 年金移行時の利率（%）
        surrender_rates: {経過年数: 返戻率} の辞書（例: {15: 0.85}）

    Returns:
        dict: 結果（年金累計額、返戻金、返戻率など）
    """

    # 総払込額
    total_paid = monthly_premium * 12 * payment_years

    # 将来一括受取額（積立利率での複利）
    lump_sum = int(total_paid * (1 + contract_rate / 100) ** payment_years)

    # 年金年額（年金移行利率を考慮）
    annual_pension = int(lump_sum * (annuity_conversion_rate / 100) / pension_years)

    # 年金累計額（年金 × 年数）
    estimated_pension = annual_pension * pension_years

    # 年金累計額の返戻率（対総払込額）
    pension_refund_rate = round(estimated_pension / total_paid * 100, 2)

    # 一括受取時の返戻率
    lump_sum_refund_rate = round(lump_sum / total_paid * 100, 2)

    # 15年時点の解約返戻金（テーブルを参照）
    surrender_rate_15 = surrender_rates.get(15, 0.0)
    refund_at_15 = int(monthly_premium * 12 * 15 * surrender_rate_15)
    refund_rate_15 = round(surrender_rate_15 * 100, 2)

    return {
        "total_paid": total_paid,
        "lump_sum_amount": lump_sum,
        "annual_pension": annual_pension,
        "estimated_pension": estimated_pension,
        "pension_refund_rate": pension_refund_rate,
        "lump_sum_refund_rate": lump_sum_refund_rate,
        "refund_on_15_years": refund_at_15,
        "refund_rate": refund_rate_15
    }

# ------------------------------------------------------------------------------
# シナリオ構築（各利率パターン）
# ------------------------------------------------------------------------------
from uuid import UUID
from datetime import datetime
from app.models.quotes import PensionQuoteScenarioModel

def build_scenario_model(
    quote_id: UUID,
    scenario_type: str,
    interest_rate: float,
    benefits: Dict[str, float]
) -> PensionQuoteScenarioModel:
    """
    PensionQuoteScenarioModel を構築するユーティリティ関数

    Parameters:
        quote_id: 見積もりID
        scenario_type: シナリオ種別（"base", "low", "high"）
        interest_rate: 利率（%）
        benefits: calculate_benefits() の出力辞書

    Returns:
        PensionQuoteScenarioModel
    """
    return PensionQuoteScenarioModel(
        quote_id=quote_id,
        scenario_type=scenario_type,
        interest_rate=interest_rate,
        estimated_pension=int(benefits["estimated_pension"]),
        pension_refund_rate=round(benefits["pension_refund_rate"], 2),
        annual_pension=int(benefits["annual_pension"]),
        lump_sum_amount=int(benefits["lump_sum_amount"]),
        lump_sum_refund_rate=round(benefits["lump_sum_refund_rate"], 2),
        refund_on_15_years=int(benefits["refund_on_15_years"]),
        refund_rate=round(benefits["refund_rate"], 2),
        note=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

# ------------------------------------------------------------------------------
# メイン処理：見積もり生成
# ------------------------------------------------------------------------------
async def calculate_quote(
    request: PensionQuoteRequestModel,
    mongo_client: AsyncIOMotorClient,
    quote_id: Optional[UUID] = None
) -> PensionQuoteCalculateResult:
    """
    個人年金保険の見積もりを生成（MongoDBの予定利率を使用）

    Parameters:
        request: 入力リクエストモデル
        mongo_client: MongoDBクライアント

    Returns:
        PensionQuoteCalculateResult
    """
    logger.info("[見積もり開始] 入力: %s", request.json())

    # ────────────────────────────────
    # Step 1: 契約日・契約年齢の算出
    # ────────────────────────────────
    today = date.today()
    contract_date = get_contract_start_date(today)
    birth_date = request.birth_date

    pension_start_age = contract_date.year - birth_date.year
    if contract_date < birth_date.replace(year=contract_date.year):
        pension_start_age -= 1

    logger.debug("[年金開始年齢] %d歳", pension_start_age)

    if pension_start_age < MIN_AGE or pension_start_age > MAX_AGE:
        logger.warning("[契約年齢エラー] %d歳", pension_start_age)
        raise HTTPException(status_code=400, detail=f"契約年齢は{MIN_AGE}〜{MAX_AGE}歳の範囲です")

    if request.payment_period_years < MIN_PAYMENT_YEARS:
        raise HTTPException(status_code=400, detail=f"払込期間は最低{MIN_PAYMENT_YEARS}年以上必要です")

    # ────────────────────────────────
    # Step 2: MongoDBから利率情報取得
    # ────────────────────────────────
    try:
        rates = await load_interest_rates(
            db=mongo_client, 
            plan_code=PLAN_CODE,
            contract_date=contract_date
        )
    except Exception:
        logger.exception("[利率取得失敗] MongoDBエラー")
        raise HTTPException(status_code=503, detail="利率情報の取得に失敗しました")

    logger.info("[利率取得] base=%.2f, low=%.2f, high=%.2f",
                rates["contract_rate"], rates["min_rate"], rates["high_rate"])

    # ────────────────────────────────
    # Step 3: 各シナリオの生成（3パターン）
    # ────────────────────────────────
    if quote_id is None:
        quote_id = uuid4()  # 新規発行用のID
        logger.info(f"[見積もりID発行]quote_id: {quote_id}")
    else:
        logger.info(f"[calculate_quote] 既存quote_idを再利用: {quote_id}")
    pension_years = request.pension_payment_years or 10  # 初期値10年

    scenarios: List[PensionQuoteScenarioModel] = []

    for scenario_type, rate_key in [("base", "contract_rate"), ("low", "min_rate"), ("high", "high_rate")]:
        rate = rates[rate_key]

        benefits = calculate_benefits(
            monthly_premium=request.monthly_premium,
            payment_years=request.payment_period_years,
            pension_years=pension_years,
            contract_rate=rate,
            annuity_conversion_rate=rates["annuity_conversion_rate"],
            surrender_rates=rates["surrender_rates"]
        )

        scenario_model = build_scenario_model(
            quote_id=quote_id,
            scenario_type=scenario_type,
            interest_rate=rate,
            benefits=benefits
        )

        scenarios.append(scenario_model)

    # ────────────────────────────────
    # Step 4: レスポンス構築
    # ────────────────────────────────
    total_paid_amount = request.monthly_premium * 12 * request.payment_period_years

    response = PensionQuoteCalculateResult(
        quote_id=quote_id,
        contract_date=contract_date,
        contract_interest_rate=rates["contract_rate"],
        total_paid_amount=total_paid_amount,
        pension_start_age=pension_start_age,
        annual_tax_deduction=MAX_ANNUAL_TAX_DEDUCTION,
        scenarios=scenarios
    )

    logger.info("[見積もり完了] quote_id=%s", quote_id)
    return response