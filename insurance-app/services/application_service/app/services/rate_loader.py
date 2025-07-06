# -*- coding: utf-8 -*-
"""
利率データ取得モジュール

- MongoDBから契約日に該当する利率情報を取得
- 契約利率、最低保証利率、および高金利シナリオ利率を提供
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from datetime import datetime, time, timezone
from typing import Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# メイン処理: 利率取得ロジック
# ------------------------------------------------------------------------------
async def load_interest_rates(
    db: AsyncIOMotorClient,
    plan_code: str,
    contract_date: datetime
) -> Dict[str, float]:
    """
    指定された契約日とプランコードに該当する利率情報をMongoDBから取得します。

    Parameters:
        db (AsyncIOMotorClient): MongoDBクライアント
        contract_date (datetime): 契約日（UTC）
        plan_code (str): 商品コード（例: "PENSION_001"）

    Returns:
        Dict[str, float]: 各利率情報を含む辞書

    Raises:
        ValueError: 利率情報が見つからない場合
        Exception: DB接続やその他の実行時例外
    """
    # --------------------------------------------------------------------------
    # 前処理: 日付の時刻とタイムゾーンを統一（UTC, 00:00:00）
    # --------------------------------------------------------------------------
    if isinstance(contract_date, datetime):
        normalized_date = contract_date.replace(hour=0, minute=0, second=0, microsecond=0)
        normalized_date = normalized_date.replace(tzinfo=timezone.utc)
    else:
        normalized_date = datetime.combine(contract_date, time.min)

    logger.info("[利率取得] MongoDBから利率取得開始: 対象日=%s", normalized_date)
    logger.debug("[利率取得] plan_code=%s, contract_date=%s", plan_code, contract_date)

    try:
        # ----------------------------------------------------------------------
        # 利率情報の取得: 指定日に有効な 'contract' タイプのレートを検索
        # ----------------------------------------------------------------------
        collection = db.get_database(config.mongodb_rate["database"]).get_collection(config.mongodb_rate["collection"])
        record: Any = await collection.find_one({
            "plan_code": plan_code,
            "start_date": {"$lte": normalized_date},
            "end_date": {"$gt": normalized_date}
        })

        logger.debug("[利率取得] record取得結果: %s", record)

        if not record:
            logger.error("[利率取得] 利率情報が見つかりません: plan_code=%s, date=%s", plan_code, normalized_date)
            raise ValueError("利率情報が見つかりません")

        logger.debug("[利率取得] 該当レコード: %s", record)

        # ----------------------------------------------------------------------
        # 利率の抽出と変換
        # ----------------------------------------------------------------------
        contract_rate = float(record.get("contract_rate"))
        min_rate = float(record.get("min_rate"))
        annuity_conversion_rate = float(record.get("annuity_conversion_rate"))
        high_rate = round(contract_rate + 0.3, 3)
        surrender_rates = record.get("surrender_rates", {})

        logger.info(
            "[利率取得] 利率取得成功: contract_rate=%.3f, min_rate=%.3f, annuity_conversion_rate=%.3f, high_rate=%.3f, surrender_rate=%s",
            contract_rate, min_rate, annuity_conversion_rate, high_rate, surrender_rates
        )

        return {
            "contract_rate": contract_rate,
            "min_rate": min_rate,
            "annuity_conversion_rate": annuity_conversion_rate,
            "high_rate": high_rate,
            "surrender_rates": surrender_rates
        }

    except Exception as e:
        # ----------------------------------------------------------------------
        # 例外処理: MongoDBエラーやレコードの不整合など
        # ----------------------------------------------------------------------
        logger.exception("[利率取得] 利率取得中に例外発生: %s", str(e))
        raise
