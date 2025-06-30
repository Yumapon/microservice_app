# -*- coding: utf-8 -*-
"""
セッション管理モジュール（Cookie + Redis + itsdangerous）
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import uuid
import json
from fastapi import Request, Response, HTTPException, status
from itsdangerous import URLSafeSerializer, BadSignature
import redis.asyncio as redis

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期化
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

# CookieとRedisのセッション管理用設定
SESSION_COOKIE_NAME = "bff_session_id"
serializer = URLSafeSerializer(config.session["secret_key"])
redis_client = redis.from_url(config.session["redis_url"])

# ------------------------------------------------------------------------------
# セッション作成：UUIDベースのセッションIDを生成し、Redisへ保存 + クッキーへ設定
# ------------------------------------------------------------------------------
async def create_session_and_set_cookie(
    response: Response, data: dict, max_age: int = 1800
):
    """
    セッションを作成し、Redisに保存した上で、Cookieを設定する

    Args:
        response (Response): レスポンスオブジェクト（Cookie設定用）
        data (dict): セッションに保存するデータ
        max_age (int): セッションの有効期限（秒）
    """
    session_id = str(uuid.uuid4())
    session_token = serializer.dumps(session_id)

    # Redisにセッションデータを保存（JSON文字列）
    await redis_client.setex(session_id, max_age, json.dumps(data))

    # Cookieに署名付きセッションIDを保存
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        httponly=True,
        secure=config.session["secure_cookie"],
        samesite="Lax",
        path="/",
        max_age=max_age,
    )

    logger.info(f"新セッション発行: {session_id} (有効期限 {max_age}秒)")

# ------------------------------------------------------------------------------
# セッション取得：CookieのトークンをデコードしてRedisから取得
# ------------------------------------------------------------------------------
async def get_session(request: Request):
    """
    リクエストからセッション情報を取得する

    Args:
        request (Request): クライアントリクエスト

    Returns:
        dict or None: セッションデータ（辞書）または存在しない場合はNone
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        logger.info("セッションIDクッキーなし")
        return None

    try:
        session_id = serializer.loads(token)
        session_data_json = await redis_client.get(session_id)
        if not session_data_json:
            logger.warning(f"RedisにセッションIDなし: {session_id}")
            return None

        logger.info(f"セッション取得成功: {session_id}")
        return json.loads(session_data_json)

    except BadSignature:
        logger.warning("セッションID署名検証失敗")
        return None

# ------------------------------------------------------------------------------
# セッション削除：RedisとCookieの両方を削除
# ------------------------------------------------------------------------------
async def clear_session(request: Request, response: Response):
    """
    セッションを削除する（Redis + Cookie）

    Args:
        request (Request): クライアントリクエスト
        response (Response): クッキー削除のためのレスポンスオブジェクト
    """
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        try:
            session_id = serializer.loads(token)
            await redis_client.delete(session_id)
            logger.info(f"Redisのセッション {session_id} を削除しました")
        except BadSignature:
            logger.warning("署名検証失敗：不正なセッショントークン")

    response.delete_cookie(SESSION_COOKIE_NAME)
    logger.info("セッションIDクッキー削除完了")