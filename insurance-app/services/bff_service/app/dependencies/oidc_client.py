# -*- coding: utf-8 -*-
"""
OIDCクライアントユーティリティ

責務:
- OpenID Connect の discovery エンドポイントから必要情報の初期化
- JWK鍵セットの取得と検証用キャッシュ
- アクセストークン（JWT）の署名とaud（クライアントID）検証
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import httpx
from jose import jwk, jwt
from jose.utils import base64url_decode


# ------------------------------------------------------------------------------
# クラス定義: OIDCClient
# ------------------------------------------------------------------------------
class OIDCClient:
    """
    OIDC Discovery & トークン署名検証を扱うクラス
    """

    def __init__(self, discovery_url, client_id, client_secret):
        """
        コンストラクタ

        Args:
            discovery_url (str): KeycloakなどのOIDCプロバイダのdiscovery URL
            client_id (str): クライアントID
            client_secret (str): クライアントシークレット
        """
        self.discovery_url = discovery_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.endpoints = {}   # discoveryで得られる各種エンドポイント群
        self.jwk_keys = {}    # kid → 公開鍵のマッピング（JWK）

    # --------------------------------------------------------------------------
    # 初期化処理: discovery → JWK取得
    # --------------------------------------------------------------------------
    async def initialize(self):
        """
        discoveryエンドポイントとJWKセットを取得して初期化する
        """
        async with httpx.AsyncClient() as client:
            # OIDC discovery endpoint を取得
            discovery = await client.get(self.discovery_url)
            discovery.raise_for_status()
            self.endpoints = discovery.json()

            # JWK Set を取得して kid をキーに保持
            jwks = await client.get(self.endpoints["jwks_uri"])
            jwks.raise_for_status()
            self.jwk_keys = {
                key["kid"]: key for key in jwks.json()["keys"]
            }

    # --------------------------------------------------------------------------
    # トークン検証処理: 署名 + audience
    # --------------------------------------------------------------------------
    def verify_token(self, token):
        """
        トークンの署名検証とaudの検証を行う

        Args:
            token (str): JWTアクセストークン

        Returns:
            dict: トークンのクレーム（payload部分）

        Raises:
            Exception: kidが不明 / 署名不正 / aud不一致など
        """
        # JWTヘッダーから kid を抽出
        header = jwt.get_unverified_header(token)
        kid = header["kid"]

        # 対応する公開鍵データを取得
        key_data = self.jwk_keys.get(kid)
        if not key_data:
            raise Exception("Unknown kid")

        # 公開鍵構築 & 署名検証
        public_key = jwk.construct(key_data)
        message, encoded_signature = token.rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode())

        if not public_key.verify(message.encode(), decoded_signature):
            raise Exception("Invalid signature")

        # クレーム検証（aud一致チェック）
        claims = jwt.get_unverified_claims(token)
        if claims["aud"] != self.client_id:
            raise Exception("Invalid audience")

        return claims
