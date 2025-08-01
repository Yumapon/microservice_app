# -*- coding: utf-8 -*-
"""
MongoDB クライアント初期化処理

FastAPI における Depends インジェクション用の非同期 MongoDB クライアントを提供します。
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定読み込み
# ------------------------------------------------------------------------------
config = Config()


# ------------------------------------------------------------------------------
# MongoDB クライアント取得関数（DI用）
# ------------------------------------------------------------------------------
def get_mongo_client() -> AsyncIOMotorClient:
    """
    FastAPI の Depends 経由で使用される MongoDB クライアントを返す

    Returns:
        AsyncIOMotorClient: 非同期MongoDBクライアントインスタンス
    """
    return AsyncIOMotorClient(
        config.mongodb["dsn"],
        uuidRepresentation="standard"
    )
