import logging
from fastapi import FastAPI
import routes
from oidc import OIDCClient
from config import Config

# 設定読み込み
config = Config()

# ログ初期化（日本語ログ）
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# OIDC初期化
oidc_client = OIDCClient(
    discovery_url=config.keycloak["discovery_url"],
    client_id=config.keycloak["client_id"],
    client_secret=config.keycloak["client_secret"]
)

app = FastAPI()
app.state.oidc_client = oidc_client
app.include_router(routes.router)

@app.on_event("startup")
async def startup_event():
    logger.info("=== アプリケーション起動開始 ===")
    await oidc_client.initialize()
    logger.info("=== OIDCディスカバリー情報と公開鍵 初期化完了 ===")

@app.get("/protected")
async def protected():
    logger.info("【API】/protected 呼び出し")
    return {"message": "これは認証保護されたAPIです。"}