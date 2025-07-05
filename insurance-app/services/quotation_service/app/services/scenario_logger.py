# -*- coding: utf-8 -*-
"""
MongoDBへのシナリオ保存処理モジュール（更新対応版）

- 保険見積もりに基づくシナリオをMongoDBに保存
- 対象quote_idに紐づく既存シナリオを削除し、新しいものに置き換える
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from app.models.quotes import PensionQuoteScenarioModel
from typing import List
from uuid import UUID

from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)

