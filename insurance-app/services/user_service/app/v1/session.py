import logging
import uuid
import json
import time
from fastapi import Request, Response, HTTPException, status
from itsdangerous import URLSafeSerializer, BadSignature
from jose import jwt
from config import Config
import redis.asyncio as redis
import httpx

logger = logging.getLogger(__name__)
config = Config()

serializer = URLSafeSerializer(config.session["secret_key"])
SESSION_COOKIE_NAME = "bff_session_id"

redis_client = redis.from_url(config.session["redis_url"])

# セッション作成
async def create_session_and_set_cookie(response: Response, data: dict):
    session_id = str(uuid.uuid4())
    session_token = serializer.dumps(session_id)

    await redis_client.setex(session_id, 1800, json.dumps(data))
    response.set_cookie(
        SESSION_COOKIE_NAME,
        session_token,
        httponly=True,
        secure=config.session["secure_cookie"],
        samesite="Lax",
        path="/"
    )
    logger.info(f"新セッション発行: {session_id}")

# セッション取得
async def get_session(request: Request):
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

# セッション削除
async def clear_session(request: Request, response: Response):
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

# アクセストークン期限確認 (5分前バッファ)
def is_token_expiring_soon(access_token: str, leeway_seconds=300):
    try:
        claims = jwt.get_unverified_claims(access_token)
        exp = claims.get("exp")
        now = int(time.time())
        if exp - now < leeway_seconds:
            logger.info(f"アクセストークン残り{exp-now}秒：更新対象")
            return True
        else:
            logger.info(f"アクセストークン残り{exp-now}秒：まだ有効")
            return False
    except Exception as e:
        logger.warning(f"トークン期限確認失敗: {e}")
        return True

# 共通認証依存関数
async def require_active_session(request: Request):
    session = await get_session(request)
    if not session:
        logger.warning("認証失敗：セッションが存在しません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証が必要です")

    if is_token_expiring_soon(session["access_token"]):
        logger.info("アクセストークン更新処理を実施")

        from oidc import OIDCClient
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
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="再認証が必要です")

            token_data = token_resp.json()
            logger.info("アクセストークン更新成功")

            # セッション更新
            session["access_token"] = token_data["access_token"]
            if token_data.get("refresh_token"):
                session["refresh_token"] = token_data["refresh_token"]

            # Redis更新
            token = request.cookies.get(SESSION_COOKIE_NAME)
            session_id = serializer.loads(token)
            await redis_client.setex(session_id, 1800, json.dumps(session))
            logger.info(f"セッション更新完了: {session_id}")

    return session
