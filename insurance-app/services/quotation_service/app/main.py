# -*- coding: utf-8 -*-
"""
FastAPI アプリケーション起動スクリプト

- MongoDB クライアントの初期化
- ルーター登録
- 設定とロギングの構成
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import asyncio
import logging

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.services.nats_subscriber import run_nats_subscriber
from app.services.nats_publisher import init_nats_connection, close_nats_connection

from app.routes import quotes
from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・構成の読み込み
# ------------------------------------------------------------------------------
config = Config()

# ------------------------------------------------------------------------------
# ログ設定（日本語対応）
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# FastAPI アプリケーション初期化
# ------------------------------------------------------------------------------
app = FastAPI(title="Quotation Service")

# ------------------------------------------------------------------------------
# ルーター登録（見積もりAPI）
# ------------------------------------------------------------------------------
app.include_router(quotes.router, prefix="/api/v1")

# ------------------------------------------------------------------------------
# スタートアップイベント: MongoDB クライアントの初期化
# ------------------------------------------------------------------------------
@app.on_event("startup")
async def startup_db_client():
    """
    アプリケーション起動時にMongoDBクライアントを初期化し、
    `app.state.mongo_client` に接続インスタンスを保持する。
    """
    logger.info("MongoDB クライアントの初期化")
    app.state.mongo_client = AsyncIOMotorClient(config.mongodb["dsn"])

# 起動時に NATS 購読を開始
@app.on_event("startup")
async def startup_event():
    logging.basicConfig(level=logging.INFO)
    asyncio.create_task(run_nats_subscriber())

@app.on_event("startup")
async def on_startup():
    await init_nats_connection()

@app.on_event("shutdown")
async def on_shutdown():
    await close_nats_connection()