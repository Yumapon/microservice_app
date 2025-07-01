# -*- coding: utf-8 -*-
"""
Keycloakを使ったJWTベースの認証・認可機構

- 認証: アクセストークンの検証とデコード
- 認可: quote_writer権限の有無チェック
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from typing import Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose.utils import base64url_decode
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import httpx

from app.config.config import Config

# ------------------------------------------------------------------------------
# ログと設定の初期化
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
config = Config()

# ------------------------------------------------------------------------------
# Keycloakに関する基本設定
# ------------------------------------------------------------------------------
keycloak_config = config.keycloak
KEYCLOAK_BASE_URL = keycloak_config["keycloak_base_url"]
CLIENT_ID = keycloak_config["client_id"]
ALGORITHM = "RS256"

JWKS_URL = f"{KEYCLOAK_BASE_URL}/protocol/openid-connect/certs"
ISSUER = KEYCLOAK_BASE_URL

# FastAPI用のOAuth2認証スキーム
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ------------------------------------------------------------------------------
# 公開鍵の取得処理（JWKからRSA公開鍵を構築）
# ------------------------------------------------------------------------------
async def get_public_key() -> rsa.RSAPublicKey:
    """
    Keycloak の JWKs エンドポイントから公開鍵を取得して構築
    """
    logger.info("KeycloakのJWK取得開始")
    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)
        if response.status_code != 200:
            logger.error("JWK取得失敗: %s", response.text)
            raise HTTPException(status_code=500, detail="JWK取得に失敗しました")

        # JWKの最初のキーを使う（必要に応じてkidで選別も可能）
        jwks = response.json()["keys"]
        key = jwks[0]

        # n, e をデコードして公開鍵を生成
        n = int.from_bytes(base64url_decode(key["n"].encode("utf-8")), "big")
        e = int.from_bytes(base64url_decode(key["e"].encode("utf-8")), "big")

        logger.info("KeycloakのJWK取得成功")
        return rsa.RSAPublicNumbers(e, n).public_key(default_backend())

# ------------------------------------------------------------------------------
# 認証処理: アクセストークンの検証とデコード
# ------------------------------------------------------------------------------
async def authenticate_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Authorizationヘッダ内のアクセストークンをKeycloakの公開鍵で検証し、デコードした内容と元トークンを返す
    """
    logger.info("アクセストークン認証開始")

    try:
        public_key = await get_public_key()

        # クレームの事前ログ出力
        unverified = jwt.get_unverified_claims(token)
        logger.info(
            "Token unverified claims: aud=%s, iss=%s",
            unverified.get("aud"), unverified.get("iss")
        )

        # トークンの検証（署名・aud・iss）
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[ALGORITHM],
            audience=CLIENT_ID,
            issuer=ISSUER,
        )

        logger.info("アクセストークン検証成功: sub=%s", payload.get("sub"))
        return {
            **payload,
            "access_token": token
        }

    except jwt.ExpiredSignatureError:
        logger.warning("アクセストークン期限切れ")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの有効期限が切れています"
        )

    except jwt.JWTClaimsError as e:
        logger.warning("トークンクレームエラー: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンのクレームが正しくありません"
        )

    except jwt.JWTError as e:
        logger.error("トークン検証失敗（JWTエラー）: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの検証に失敗しました"
        )

    except Exception as e:
        logger.error("トークン検証失敗（一般例外）: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンの検証中にエラーが発生しました"
        )

# ------------------------------------------------------------------------------
# 認可: application_writer権限を保持しているかの確認
# ------------------------------------------------------------------------------
def has_application_write_permission(token: dict) -> bool:
    """
    tokenに 'application_writer' 権限が含まれているかを判定
    """
    try:
        roles = token.get("resource_access", {}) \
                     .get(CLIENT_ID, {}) \
                     .get("roles", [])
        return "application_writer" in roles
    except Exception:
        logger.exception("application_writer権限チェック中に例外発生")
        return False
    
# ------------------------------------------------------------------------------
# 認可: application_reader権限を保持しているかの確認
# ------------------------------------------------------------------------------
def has_application_read_permission(token: dict) -> bool:
    """
    tokenに 'application_reader' 権限が含まれているかを判定
    """
    try:
        roles = token.get("resource_access", {}) \
                     .get(CLIENT_ID, {}) \
                     .get("roles", [])
        return "application_reader" in roles
    except Exception:
        logger.exception("application_reader権限チェック中に例外発生")
        return False

# ------------------------------------------------------------------------------
# FastAPI依存関数: application_writer権限を強制する
# ------------------------------------------------------------------------------
async def require_application_write_permission(
    token: dict = Depends(authenticate_user)
) -> dict:
    """
    application_writer権限を持つユーザのみを許可する依存関数
    """
    if not has_application_write_permission(token):
        logger.warning("application_writer権限なし: sub=%s", token.get("sub"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="application_writer権限がありません"
        )

    logger.info("application_writer権限確認済み: sub=%s", token.get("sub"))
    return token

# ------------------------------------------------------------------------------
# FastAPI依存関数: application_reader権限を強制する
# ------------------------------------------------------------------------------
async def require_application_read_permission(
    token: dict = Depends(authenticate_user)
) -> dict:
    """
    application_reader権限を持つユーザのみを許可する依存関数
    """
    if not has_application_read_permission(token):
        logger.warning("application_reader権限なし: sub=%s", token.get("sub"))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="application_reader権限がありません"
        )

    logger.info("application_reader権限確認済み: sub=%s", token.get("sub"))
    return token
