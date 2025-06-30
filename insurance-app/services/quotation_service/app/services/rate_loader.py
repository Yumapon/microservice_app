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
from datetime import datetime, timezone
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
    contract_date: datetime
) -> Dict[str, float]:
    """
    指定された契約日に該当する予定利率・最低保証利率をMongoDBから取得します。
    高金利シナリオ（契約時利率 + 0.3%）はロジック内で導出されます。

    Parameters:
        db (AsyncIOMotorClient): MongoDBクライアント
        contract_date (datetime): 契約日（UTC）

    Returns:
        Dict[str, float]: 契約利率、最低保証利率、高金利シナリオ利率を含む辞書

    Raises:
        ValueError: 利率情報が見つからない場合
        Exception: DB接続やその他の実行時例外
    """
    # --------------------------------------------------------------------------
    # 前処理: 日付の時刻とタイムゾーンを統一（UTC, 00:00:00）
    # --------------------------------------------------------------------------
    contract_date = contract_date.replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
    )
    logger.info("[利率取得] MongoDBから利率取得開始: 対象日=%s", contract_date)

    try:
        # ----------------------------------------------------------------------
        # 利率情報の取得: 指定日に有効な 'contract' タイプのレートを検索
        # ----------------------------------------------------------------------
        collection = db.get_database(config.mongodb["database"]).get_collection(config.mongodb["collection"])
        record: Any = await collection.find_one({
            "start_date": {"$lte": contract_date},
            "end_date": {"$gte": contract_date},
            "rate_type": "contract",
            "product_type": "pension"
        })

        if not record:
            logger.error("[利率取得] 利率情報が見つかりません: contract_date=%s", contract_date)
            raise ValueError("利率情報が見つかりません")

        logger.debug("[利率取得] 該当レコード: %s", record)

        # ----------------------------------------------------------------------
        # 利率の抽出と変換
        # ----------------------------------------------------------------------
        contract_rate = float(record.get("rate"))
        min_rate = float(record.get("guaranteed_minimum_rate"))
        high_rate = round(contract_rate + 0.3, 3)  # 高金利シナリオ

        logger.info(
            "[利率取得] 利率取得成功: contract_rate=%.3f, min_rate=%.3f, high_rate=%.3f",
            contract_rate, min_rate, high_rate
        )

        return {
            "contract_rate": contract_rate,
            "min_rate": min_rate,
            "high_rate": high_rate
        }

    except Exception as e:
        # ----------------------------------------------------------------------
        # 例外処理: MongoDBエラーやレコードの不整合など
        # ----------------------------------------------------------------------
        logger.exception("[利率取得] 利率取得中に例外発生: %s", str(e))
        raise
