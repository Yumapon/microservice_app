# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりロジック（MongoDBから利率を取得し、複数シナリオで返却）
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from datetime import date, timedelta
import logging

from motor.motor_asyncio import AsyncIOMotorClient

from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    PensionScenarioResultModel,
)

# ------------------------------------------------------------------------------
# ログ設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------
# メイン処理：個人年金保険の見積もりを計算
# ------------------------------------------------------------------------------
async def calculate_quote(
    user_input: PensionQuoteRequestModel,
    mongo_client: AsyncIOMotorClient
) -> PensionQuoteResponseModel:
    """
    見積もりシミュレーションの主処理。
    利率・税制適格性に応じた3シナリオ（高金利・標準・最低保証）を返却。
    """

    # --------------------------------------------------------------------------
    # 契約開始日（翌月1日）を算出
    # --------------------------------------------------------------------------
    today = date.today()
    contract_start_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1)

    # --------------------------------------------------------------------------
    # MongoDBから該当プラン情報を取得
    # --------------------------------------------------------------------------
    db = mongo_client["insurance"]
    collection = db["public_plans"]
    plan_doc = await collection.find_one({
        "product_type": "pension",
        "contract_start_date": str(contract_start_date)
    })

    if not plan_doc:
        logger.warning(
            "MongoDBに利率情報が見つかりません: contract_start_date=%s",
            contract_start_date
        )
        raise ValueError("利率情報が見つかりません")

    # --------------------------------------------------------------------------
    # 利率情報の読み出し・補正
    # --------------------------------------------------------------------------
    base_interest_rate = plan_doc["base_interest_rate"] / 100  # 例: 1.2 → 0.012
    min_interest_rate = plan_doc["min_interest_rate"] / 100
    high_interest_rate = min(base_interest_rate + 0.003, 0.03)  # 上限 3%

    # --------------------------------------------------------------------------
    # 払込総額・年金開始年齢を計算
    # --------------------------------------------------------------------------
    total_paid = user_input.monthly_premium * 12 * user_input.payment_period_years
    pension_start_age = user_input.payment_period_years + (today.year - user_input.birth_date.year)

    # --------------------------------------------------------------------------
    # シナリオシミュレーション用内部関数
    # --------------------------------------------------------------------------
    def simulate(interest_rate: float) -> PensionScenarioResultModel:
        refund_multiplier = (1 + interest_rate) ** user_input.payment_period_years
        total_refund = int(total_paid * refund_multiplier)
        annual_pension = int(total_refund / 10)  # 年金10年間
        refund_after_15 = int(
            total_paid * (1 + interest_rate) ** min(15, user_input.payment_period_years)
        )
        refund_rate = round(total_refund / total_paid * 100, 2)

        return PensionScenarioResultModel(
            interest_rate=interest_rate * 100,
            total_paid=total_paid,
            total_refund=total_refund,
            annual_pension=annual_pension,
            refund_after_15_years=refund_after_15,
            refund_rate=refund_rate
        )

    # --------------------------------------------------------------------------
    # シナリオ別の見積もり結果を構築
    # --------------------------------------------------------------------------
    scenarios = [
        simulate(high_interest_rate),
        simulate(base_interest_rate),
        simulate(min_interest_rate)
    ]

    # --------------------------------------------------------------------------
    # 税控除関連の算出（仮）
    # --------------------------------------------------------------------------
    tax_deduction_amount = 40000 if user_input.tax_deduction_opt_in else 0
    tax_effect = "控除あり（最大4万円）" if tax_deduction_amount else "控除なし"

    # --------------------------------------------------------------------------
    # レスポンスモデルを構築して返却
    # --------------------------------------------------------------------------
    return PensionQuoteResponseModel(
        contract_start_date=contract_start_date,
        base_interest_rate=base_interest_rate * 100,
        tax_deduction_amount=tax_deduction_amount,
        payment_period_years=user_input.payment_period_years,
        pension_start_age=pension_start_age,
        tax_effect=tax_effect,
        scenarios=scenarios
    )
