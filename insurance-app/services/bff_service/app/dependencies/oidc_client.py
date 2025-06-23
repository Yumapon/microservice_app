import httpx
from jose import jwk, jwt
from jose.utils import base64url_decode

class OIDCClient:
    def __init__(self, discovery_url, client_id, client_secret):
        self.discovery_url = discovery_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.endpoints = {}
        self.jwk_keys = {}

    async def initialize(self):
        async with httpx.AsyncClient() as client:
            discovery = await client.get(self.discovery_url)
            discovery.raise_for_status()
            self.endpoints = discovery.json()

            jwks = await client.get(self.endpoints["jwks_uri"])
            jwks.raise_for_status()
            self.jwk_keys = {key["kid"]: key for key in jwks.json()["keys"]}

    def verify_token(self, token):
        header = jwt.get_unverified_header(token)
        kid = header["kid"]
        key_data = self.jwk_keys.get(kid)
        if not key_data:
            raise Exception("Unknown kid")

        public_key = jwk.construct(key_data)
        message, encoded_signature = token.rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode())

        if not public_key.verify(message.encode(), decoded_signature):
            raise Exception("Invalid signature")

        claims = jwt.get_unverified_claims(token)
        if claims["aud"] != self.client_id:
            raise Exception("Invalid audience")

        return claims