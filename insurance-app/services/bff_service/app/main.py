# -*- coding: utf-8 -*-
"""
アプリケーションのエントリポイント
- FastAPIアプリ初期化
- ルーター設定
- OIDCクライアント初期化
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import (
    api_synthesis, 
    api_proxy,
    auth 
)
from app.dependencies.oidc_client import OIDCClient

from app.config.config import Config

# ------------------------------------------------------------------------------
# ログ設定
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 設定読み込み
# ------------------------------------------------------------------------------
config = Config()

# ------------------------------------------------------------------------------
# OIDCクライアント初期化
# ------------------------------------------------------------------------------
oidc_client = OIDCClient(
    discovery_url=config.keycloak["discovery_url"],
    client_id=config.keycloak["client_id"],
    client_secret=config.keycloak["client_secret"]
)

# ------------------------------------------------------------------------------
# FastAPIアプリケーション定義
# ------------------------------------------------------------------------------
app = FastAPI(title="Public Insurance Plans Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # フロントのURLを指定
    allow_credentials=True,  # Cookieを使うので必要
    allow_methods=["*"],
    allow_headers=["*"],
)

# OIDCクライアントをアプリケーションステートに保持
app.state.oidc_client = oidc_client

# ------------------------------------------------------------------------------
# ルーター登録
# ------------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(api_synthesis.router, prefix="/api/v1/bff")
app.include_router(api_proxy.router, prefix="/api/v1/bff")

# ------------------------------------------------------------------------------
# アプリケーション起動時イベント
# ------------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """
    アプリケーション起動時にOIDC情報を初期化する
    """
    logger.info("=== アプリケーション起動開始 ===")
    await oidc_client.initialize()
    logger.info("=== OIDCディスカバリー情報と公開鍵 初期化完了 ===")
