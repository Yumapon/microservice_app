# -*- coding: utf-8 -*-
"""
アクセストークンのリフレッシュ処理

責務:
- セッションからリフレッシュトークンを取り出し、OIDCプロバイダに対して
  新たなアクセストークンを取得する
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import httpx

# ------------------------------------------------------------------------------
# ロガー初期化
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# 関数定義：リフレッシュトークンによるアクセストークン再取得
# ------------------------------------------------------------------------------
async def refresh_token(session_data, oidc_client, config):
    """
    OIDCのリフレッシュトークンを使ってアクセストークンを再取得する

    Args:
        session_data (dict): セッション内のトークン情報（access_token, refresh_tokenなど）
        oidc_client (OIDCClient): OIDCのエンドポイント情報を保持したクライアント
        config (Config): クライアントID、シークレットなどの設定情報

    Returns:
        dict or None: トークン情報（access_token, refresh_tokenなど） or None（失敗時）
    """
    refresh_token = session_data.get("refresh_token")
    if not refresh_token:
        logger.warning("リフレッシュトークンが存在しません")
        return None

    # トークン再取得に必要なパラメータを構築
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": config.keycloak["client_id"],
        "client_secret": config.keycloak["client_secret"]
    }

    # 非同期HTTPクライアントを使ってトークンエンドポイントにリクエスト
    async with httpx.AsyncClient() as client:
        response = await client.post(
            oidc_client.endpoints["token_endpoint"],
            data=data
        )

        if response.status_code != 200:
            logger.warning("リフレッシュトークン更新失敗")
            return None

        logger.info("アクセストークン更新成功")
        return response.json()
