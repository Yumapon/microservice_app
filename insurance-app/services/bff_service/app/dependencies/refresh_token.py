import httpx
import logging

logger = logging.getLogger(__name__)

async def refresh_token(session_data, oidc_client, config):
    refresh_token = session_data.get("refresh_token")
    if not refresh_token:
        logger.warning("リフレッシュトークンが存在しません")
        return None

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": config.keycloak["client_id"],
        "client_secret": config.keycloak["client_secret"]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(oidc_client.endpoints["token_endpoint"], data=data)

        if response.status_code != 200:
            logger.warning("リフレッシュトークン更新失敗")
            return None

        logger.info("アクセストークン更新成功")
        return response.json()
