import logging
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from urllib.parse import urlencode
from app.dependencies.session_manager import create_session_and_set_cookie, clear_session, get_session
from app.config.config import Config
import json
import base64

logger = logging.getLogger(__name__)
router = APIRouter()
config = Config()

def encode_state(state_dict):
    json_str = json.dumps(state_dict)
    return base64.urlsafe_b64encode(json_str.encode()).decode()

def decode_state(state_str):
    try:
        json_str = base64.urlsafe_b64decode(state_str.encode()).decode()
        return json.loads(json_str)
    except Exception as e:
        logger.warning(f"stateデコード失敗: {e}")
        return {}

@router.get("/login")
async def login(request: Request, remember_me: bool = False):
    logger.info("【API】/auth/login 呼び出し")
    session = await get_session(request)
    if session:
        logger.info("セッションあり: 既にログイン済みユーザー")
        return JSONResponse(content={"message": "既にログイン済み", "user": session["user_info"]})

    authorize_url = request.app.state.oidc_client.endpoints["authorization_endpoint"]
    state_param = encode_state({"remember_me": remember_me})

    params = {
        "client_id": config.keycloak["client_id"],
        "response_type": "code",
        "scope": "openid profile email",
        "redirect_uri": config.keycloak["redirect_uri"],
        "state": state_param
    }
    redirect_url = f"{authorize_url}?{urlencode(params)}"
    logger.info("Keycloakの認証画面にリダイレクト")
    return RedirectResponse(url=redirect_url)

@router.get("/callback")
async def auth_callback(request: Request, code: str, state: str = None):
    logger.info("【API】/auth/callback 呼び出し")
    oidc_client = request.app.state.oidc_client

    logger.info(f"認可コード受信: {code}")
    state_data = decode_state(state) if state else {}
    remember_me = state_data.get("remember_me", False)

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config.keycloak["redirect_uri"],
        "client_id": config.keycloak["client_id"],
        "client_secret": config.keycloak["client_secret"]
    }

    async with httpx.AsyncClient() as client:
        logger.info("Keycloakにトークン取得リクエスト送信")
        token_resp = await client.post(oidc_client.endpoints["token_endpoint"], data=data)
        token_resp.raise_for_status()
        token_data = token_resp.json()
        logger.info("アクセストークン取得成功")

        userinfo_resp = await client.get(
            oidc_client.endpoints["userinfo_endpoint"],
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        userinfo_resp.raise_for_status()
        userinfo_data = userinfo_resp.json()
        logger.info(f"ユーザ情報取得成功: サブID={userinfo_data['sub']}")

    session_data = {
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token"),
        "user_info": userinfo_data
    }

    response = RedirectResponse(url="/api/v1/top")
    # remember_me に応じて有効期限設定（例: 30日 or 30分）
    max_age = config.session["rememberme_ttl"] if remember_me else config.session["normal_ttl"]
    await create_session_and_set_cookie(response, session_data, max_age)
    logger.info("セッション保存・クッキーセット完了 -> /topへリダイレクト")
    return response

@router.post("/logout")
async def logout(request: Request):
    logger.info("【API】/auth/logout 呼び出し")
    session = await get_session(request)
    if not session:
        logger.warning("ログアウト要求：セッションなし -> そのまま成功返却")
        return JSONResponse(content={"message": "ログアウト完了"})

    refresh_token = session.get("refresh_token")
    if refresh_token:
        oidc_client = request.app.state.oidc_client
        logout_url = oidc_client.endpoints["end_session_endpoint"]
        data = {
            "client_id": config.keycloak["client_id"],
            "client_secret": config.keycloak["client_secret"],
            "refresh_token": refresh_token
        }
        async with httpx.AsyncClient() as client:
            try:
                logger.info("Keycloakにトークン失効要求送信")
                resp = await client.post(logout_url, data=data)
                resp.raise_for_status()
                logger.info("Keycloak側トークン失効成功")
            except Exception as e:
                logger.warning(f"KeycloakログアウトAPI失敗: {e}")

    response = JSONResponse(content={"message": "ログアウト完了"})
    await clear_session(request, response)
    logger.info("セッション削除・クッキー削除完了")
    return response