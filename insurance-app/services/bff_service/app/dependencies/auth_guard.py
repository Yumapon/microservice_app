import logging
import time
import json
from jose import jwt
from fastapi import Request, HTTPException, status
from app.dependencies.refresh_token import refresh_token
from app.dependencies.oidc_client import OIDCClient
from app.dependencies.session_manager import get_session
from itsdangerous import URLSafeSerializer, BadSignature
import httpx
from app.config.config import Config
import redis.asyncio as redis

logger = logging.getLogger(__name__)
config = Config()

SESSION_COOKIE_NAME = "bff_session_id"

async def get_session_data(request: Request):
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

async def get_valid_session(request: Request):
    session = await get_session(request)
    if not session:
        logger.warning("認証失敗：セッションが存在しません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="認証が必要です")

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
