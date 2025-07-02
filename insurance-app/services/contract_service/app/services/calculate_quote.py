# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりロジック

- 保険契約日計算
- 将来の受取金額や控除額のシミュレーション
- MongoDBからの利率取得を伴う
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Dict

from motor.motor_asyncio import AsyncIOMotorClient

from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    PensionQuoteScenarioModel
)
from app.services.rate_loader import load_interest_rates

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 契約開始日ロジック
# ------------------------------------------------------------------------------
def get_contract_start_date(today: datetime) -> datetime:
    """
    毎月1日始まりで契約日を算出（時刻を常に00:00:00に設定）

    Parameters:
        today (datetime): 現在日付

    Returns:
        datetime: 契約開始日（翌月1日）
    """
    logger.debug("[契約日計算] 今日の日付: %s", today)
    if today.day == 1:
        result = today.replace(hour=0, minute=0, second=0, microsecond=0)
        logger.debug("[契約日確定] 本日が1日のためそのまま採用: %s", result)
        return result
    next_month = today.replace(day=1) + timedelta(days=32)
    result = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logger.debug("[契約日確定] 翌月1日を採用: %s", result)
    return result

# ------------------------------------------------------------------------------
# 受取年金や返戻金の計算
# ------------------------------------------------------------------------------
def calculate_benefits(monthly_premium: int, years: int, rate: float) -> Dict[str, float]:
    """
    将来受け取り金額などを計算

    Parameters:
        monthly_premium (int): 月額保険料
        years (int): 払込期間（年）
        rate (float): 年利率（例: 0.01 = 1%）

    Returns:
        dict: 年金額、累計、返戻金など
    """
    logger.debug("[給付計算] 入力: 月額=%d, 年数=%d, 利率=%.4f", monthly_premium, years, rate)
    total_paid = monthly_premium * 12 * years
    lump_sum = int(total_paid * (1 + rate) ** years)
    annual_pension = int(lump_sum // 10)  # 10年受取と仮定
    refund_at_15 = int(total_paid * (1 + rate) ** min(years, 15))
    refund_rate = round(refund_at_15 / (monthly_premium * 12 * 15) * 100, 2)

    logger.debug("[給付計算結果] total_paid=%d, lump_sum=%d, annual_pension=%d, refund_at_15=%d, refund_rate=%.2f%%",
                 total_paid, lump_sum, annual_pension, refund_at_15, refund_rate)

    return {
        "rate": rate,
        "total_paid": total_paid,
        "annual_pension": annual_pension,
        "lump_sum": lump_sum,
        "refund_at_15": refund_at_15,
        "refund_rate": refund_rate
    }

# ------------------------------------------------------------------------------
# シナリオ構築処理
# ------------------------------------------------------------------------------
def build_scenario(
    scenario_name: str,
    rate: float,
    monthly_premium: int,
    payment_years: int
) -> PensionQuoteScenarioModel:
    """
    各利率パターン（シナリオ）の見積もりを構築

    Parameters:
        scenario_name (str): シナリオ名
        rate (float): 利率（%表記）
        monthly_premium (int): 月額保険料
        payment_years (int): 支払い期間（年）

    Returns:
        PensionQuoteScenarioModel: シナリオ見積もりモデル
    """
    logger.debug("[シナリオ構築] %s: 利率=%.2f%%, 保険料=%d, 年数=%d", scenario_name, rate, monthly_premium, payment_years)
    total_paid = monthly_premium * 12 * payment_years
    total_refund_amount = round(total_paid * (1 + rate / 100))
    annual_annuity = round(total_refund_amount / 10)  # 例：10年分割支給
    lump_sum_amount = total_refund_amount
    refund_on_15_years = round(monthly_premium * 12 * 15 * (1 + rate / 100))
    refund_rate_on_15_years = round(
        refund_on_15_years / (monthly_premium * 12 * 15) * 100, 1
    )

    logger.debug("[シナリオ結果] %s: refund=%d, annuity=%d, refund15=%d, rate15=%.1f%%",
                 scenario_name, total_refund_amount, annual_annuity, refund_on_15_years, refund_rate_on_15_years)

    return PensionQuoteScenarioModel(
        scenario_name=scenario_name,
        assumed_interest_rate=rate,
        total_refund_amount=total_refund_amount,
        annual_annuity=annual_annuity,
        lump_sum_amount=lump_sum_amount,
        refund_on_15_years=refund_on_15_years,
        refund_rate_on_15_years=refund_rate_on_15_years
    )

# ------------------------------------------------------------------------------
# メイン処理：見積もり計算
# ------------------------------------------------------------------------------
async def calculate_quote(
    request: PensionQuoteRequestModel,
    mongo_client: AsyncIOMotorClient,
    user_id: str
) -> PensionQuoteResponseModel:
    """
    個人年金保険の見積もりシミュレーションを行う

    Parameters:
        request (PensionQuoteRequestModel): ユーザー入力情報
        mongo_client (AsyncIOMotorClient): MongoDBクライアント

    Returns:
        PensionQuoteResponseModel: 見積もり結果
    """
    logger.info("[見積もり開始] user_id=%s 入力=%s", user_id, request.json())

    # 契約開始日を計算
    contract_date = get_contract_start_date(datetime.today())
    logger.info("[契約日決定] %s", contract_date)

    # 利率情報をMongoDBから取得
    rates = await load_interest_rates(mongo_client, contract_date)
    logger.info("[利率取得成功] contract_rate=%.2f%%, min_rate=%.2f%%, high_rate=%.2f%%",
                rates["contract_rate"], rates["min_rate"], rates["high_rate"])

    # 総支払額、年金開始年齢、控除額などの算出
    total_paid_amount = request.monthly_premium * 12 * request.payment_period_years
    logger.debug("[支払額算出] 月額=%d × 12 × 年数=%d → %d",
                 request.monthly_premium, request.payment_period_years, total_paid_amount)

    pension_start_age = contract_date.year - request.birth_date.year

    # birth_dateをdatetime.dateに変換（必要であれば）
    if hasattr(request.birth_date, "date"):
        birth_date_for_compare = request.birth_date.replace(year=contract_date.year).date()
    else:
        birth_date_for_compare = request.birth_date.replace(year=contract_date.year)

    if contract_date.date() < birth_date_for_compare:
        pension_start_age -= 1
        logger.debug("[年齢調整] 契約日が誕生日前のため年齢-1")

    logger.debug("[年金開始年齢] %d", pension_start_age)

    annual_tax_deduction = 40000  # 仮の年間控除額
    logger.debug("[控除額仮設定] 年間控除: %d", annual_tax_deduction)

    # 複数シナリオを構築（標準、最低保証、高金利）
    scenarios = [
        build_scenario(
            "標準",
            rates["contract_rate"],
            request.monthly_premium,
            request.payment_period_years
        ),
        build_scenario(
            "最低保証",
            rates["min_rate"],
            request.monthly_premium,
            request.payment_period_years
        ),
        build_scenario(
            "高金利",
            rates["high_rate"],
            request.monthly_premium,
            request.payment_period_years
        )
    ]

    # 見積もりレスポンス構築
    response = PensionQuoteResponseModel(
        quote_id=str(uuid4()),
        user_id=user_id,
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
