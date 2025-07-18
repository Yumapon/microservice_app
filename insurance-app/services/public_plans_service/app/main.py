from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

import logging

from app.routes import plans
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
app.include_router(plans.router, prefix="/api/v1")

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
