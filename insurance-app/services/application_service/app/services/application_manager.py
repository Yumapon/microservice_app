# -*- coding: utf-8 -*-
"""
保険申込処理ロジック
- quotation_service から見積もりを取得・検証・状態変更
- PostgreSQL に申込レコードを保存
"""

import logging
import uuid
import httpx
import asyncpg
from datetime import datetime

from app.config.config import Config
from app.models.applications import ApplicationResponseModel

logger = logging.getLogger(__name__)
config = Config()

# ---------------------------------------------------------------------
# 見積もり取得
# ---------------------------------------------------------------------
async def get_quote_from_quotation_service(quote_id: str, access_token: str) -> dict:
    """
    quotation_service から見積もり情報を取得

    Parameters:
        quote_id (str): 対象の見積もりID
        access_token (str): アクセストークン

    Returns:
        dict: 見積もり情報（JSON）

    Raises:
        httpx.HTTPStatusError: quotation_service エラー時
    """
    base_url = config.services["quotation_service_url"]

    async with httpx.AsyncClient() as client:
        logger.info("quotation_service から見積もり取得: quote_id=%s", quote_id)
        res = await client.get(
            f"{base_url}/api/v1/my/quotes/{quote_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        res.raise_for_status()
        return res.json()

# ---------------------------------------------------------------------
# 申込処理メイン関数
# ---------------------------------------------------------------------
async def create_application(user_id: str, quote: dict, access_token: str) -> ApplicationResponseModel:
    """
    取得済みの見積もりデータをもとに申込処理を行う

    Parameters:
        user_id (str): ユーザーID
        quote (dict): quotation_service から取得済みの見積もりデータ

    Returns:
        ApplicationResponseModel: 申込完了レスポンス
    """
    quote_id = quote.get("quote_id")
    if quote.get("user_id") != user_id:
        raise ValueError("他人の見積もりに対して申込処理はできません")

    if quote.get("contract_date") is None:
        raise ValueError("見積もりに契約日が設定されていません")

    # Step 1: quotation_service に PUT で状態を applied に更新
    base_url = config.services["quotation_service_url"]
    async with httpx.AsyncClient() as client:
        logger.info("見積もり状態を applied に更新: quote_id=%s", quote_id)
        res = await client.put(
            f"{base_url}/api/v1/my/quotes/{quote_id}", 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        res.raise_for_status()

    # Step 2: PostgreSQL に申込情報を保存
    application_id = str(uuid.uuid4())
    dsn = config.postgres["dsn"]
    conn = await asyncpg.connect(dsn=dsn)
    try:
        await conn.execute("""
            INSERT INTO applications (
                application_id,
                quote_id,
                user_id,
                application_status,
                user_consent,
                applied_at
            ) VALUES (
                $1, $2, $3, $4, $5, $6
            )
        """, application_id, quote_id, user_id, "applied", True, datetime.utcnow())
    finally:
        await conn.close()

    return ApplicationResponseModel(
        application_id=application_id,
        quote_id=quote_id,
        status="applied"
    )

