# -*- coding: utf-8 -*-
"""
セッション管理・アクセストークン更新のユーティリティ関数群

主な責務：
- Cookie からセッションIDを取得してセッションを検証
- アクセストークンの有効期限チェック
- 必要に応じたトークンのリフレッシュとセッションの更新
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import time
import json

import httpx
import redis.asyncio as redis
from jose import jwt
from fastapi import Request, HTTPException, status
from itsdangerous import URLSafeSerializer

from app.config.config import Config
from app.dependencies.oidc_client import OIDCClient
from app.dependencies.session_manager import get_session

# ------------------------------------------------------------------------------
# 定数・設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()
SESSION_COOKIE_NAME = "bff_session_id"
redis_client = redis.from_url(config.session["redis_url"])

# ------------------------------------------------------------------------------
# セッションデータ取得処理（CookieからセッションIDを取得 → Redisから復元）
# ------------------------------------------------------------------------------
async def get_session_data(request: Request):
    """
    CookieからセッションIDを取得し、Redisからセッションデータを取得

    Raises:
        HTTPException(401): セッションが存在しない、または期限切れ

    Returns:
        (session_id, session_data): タプルでセッションIDと中身を返す
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        logger.warning("セッションIDがありません")
        raise HTTPException(status_code=401, detail="ログインが必要です")

    session_manager = request.app.state.session_manager
    session_data = await session_manager.get_session(session_id)
    if not session_data:
        logger.warning("セッションが無効です")
        raise HTTPException(status_code=401, detail="セッション期限切れ")

    return session_id, session_data

# ------------------------------------------------------------------------------
# アクセストークンの期限切れチェック（バッファ時間を考慮）
# ------------------------------------------------------------------------------
def is_token_expiring_soon(access_token: str, leeway_seconds: int = 300):
    """
    アクセストークンがまもなく失効するかを判定

    Args:
        access_token (str): JWT形式のアクセストークン
        leeway_seconds (int): 残り何秒未満なら「まもなく失効」とみなすか（デフォルト5分）

    Returns:
        bool: True＝期限間近、False＝まだ有効
    """
    try:
        claims = jwt.get_unverified_claims(access_token)
        exp = claims.get("exp")
        now = int(time.time())
        remaining = exp - now
        if remaining < leeway_seconds:
            logger.info(f"アクセストークン残り{remaining}秒：更新対象")
            return True
        else:
            logger.info(f"アクセストークン残り{remaining}秒：まだ有効")
            return False
    except Exception as e:
        logger.warning(f"トークン期限確認失敗: {e}")
        return True  # 失敗時は失効とみなす

# ------------------------------------------------------------------------------
# アクセストークンが期限切れ間近な場合、更新してセッションに反映
# ------------------------------------------------------------------------------
async def get_valid_session(request: Request):
    """
    セッションが有効であり、アクセストークンが失効していれば更新

    Raises:
        HTTPException(401): セッションが無効、またはリフレッシュ失敗

    Returns:
        dict: 最新状態のセッションデータ
    """
    session = await get_session(request)
    if not session:
        logger.warning("認証失敗：セッションが存在しません")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証が必要です"
        )

    if is_token_expiring_soon(session["access_token"]):
        logger.info("アクセストークン更新処理を実施")
        oidc_client: OIDCClient = request.app.state.oidc_client

        data = {
            "grant_type": "refresh_token",
            "refresh_token": session["refresh_token"],
            "client_id": config.keycloak["client_id"],
            "client_secret": config.keycloak["client_secret"]
        }

        async with httpx.AsyncClient() as client:
            token_resp = await client.post(oidc_client.endpoints["token_endpoint"], data=data)
            if token_resp.status_code != 200:
                logger.warning("リフレッシュトークン失敗：認証エラー")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="再認証が必要です"
                )

            token_data = token_resp.json()
            logger.info("アクセストークン更新成功")

            # セッションの内容を更新
            session["access_token"] = token_data["access_token"]
            if token_data.get("refresh_token"):
                session["refresh_token"] = token_data["refresh_token"]

            # Redisのセッションも更新
            serializer = URLSafeSerializer(config.session["secret_key"])
            token = request.cookies.get(SESSION_COOKIE_NAME)
            session_id = serializer.loads(token)
            await redis_client.setex(session_id, 1800, json.dumps(session))
            logger.info(f"セッション更新完了: {session_id}")

    return session