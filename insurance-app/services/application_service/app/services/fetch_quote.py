# -*- coding: utf-8 -*-
"""
quotation_service から見積もりを取得するユーティリティ
"""

import logging
import httpx
from uuid import UUID
from typing import Dict

from app.config.config import Config
from fastapi import HTTPException

logger = logging.getLogger(__name__)
config = Config()

async def fetch_quote_by_id(quote_id: UUID, access_token: str) -> Dict:
    """
    quotation_service に HTTP GET を送り、指定 quote_id の見積もりを取得する

    Parameters:
        quote_id (UUID): 見積もりID
        access_token (str): Bearerトークン

    Returns:
        Dict: quotation_service から返された見積もりJSON

    Raises:
        HTTPException: quotation_serviceからエラーが返された場合
    """
    url = f"{config.services['quotation_service_url']}/api/v1/my/quotes/{quote_id}"
    headers = {"Authorization": f"Bearer {access_token}"}

    logger.info(f"[外部見積取得] URL: {url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"[見積取得失敗] status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積もり取得に失敗しました")

        quote_data = response.json()
        logger.info(f"quote_data: {quote_data}")
        logger.info(f"[見積取得成功] quote_id={quote_data.get('quote_id')}")
        return quote_data

    except Exception as e:
        logger.exception(f"[見積取得例外] {e}")
        raise HTTPException(status_code=500, detail="見積もり取得中にエラーが発生しました")