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
    if today.day == 1:
        return today.replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = today.replace(day=1) + timedelta(days=32)
    return next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

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
    total_paid = monthly_premium * 12 * years
    lump_sum = int(total_paid * (1 + rate) ** years)
    annual_pension = int(lump_sum // 10)  # 10年受取と仮定
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
    total_paid = monthly_premium * 12 * payment_years
    total_refund_amount = round(total_paid * (1 + rate / 100))
    annual_annuity = round(total_refund_amount / 10)  # 例：10年分割支給
    lump_sum_amount = total_refund_amount
    refund_on_15_years = round(monthly_premium * 12 * 15 * (1 + rate / 100))
    refund_rate_on_15_years = round(
        refund_on_15_years / (monthly_premium * 12 * 15) * 100, 1
    )

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
    logger.info("[見積もり開始] ユーザー入力: %s", request.json())

    # 契約開始日を計算
    contract_date = get_contract_start_date(datetime.today())
    logger.info("[契約日確定] 契約開始日: %s", contract_date)

    # 利率情報をMongoDBから取得
    rates = await load_interest_rates(mongo_client, contract_date)
    logger.debug("[利率取得済] rates: %s", rates)

    # 総支払額、年金開始年齢、控除額などの算出
    total_paid_amount = request.monthly_premium * 12 * request.payment_period_years

    pension_start_age = contract_date.year - request.birth_date.year

    # birth_dateをdatetime.dateに変換（必要であれば）
    if hasattr(request.birth_date, "date"):
        birth_date_for_compare = request.birth_date.replace(year=contract_date.year).date()
    else:
        birth_date_for_compare = request.birth_date.replace(year=contract_date.year)

    if contract_date.date() < birth_date_for_compare:
        pension_start_age -= 1
    annual_tax_deduction = 40000  # 仮の年間控除額

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