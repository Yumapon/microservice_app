# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりAPIエンドポイント
"""

import logging
from fastapi import APIRouter, Depends, Path, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

from app.dependencies.auth import require_quote_write_permission
from app.dependencies.get_mongo_client import get_mongo_client
from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    QuoteStateUpdateModel
)
from app.services.calculate_quote import calculate_quote
from app.services.quote_manager import (
    get_quotes_by_user_id,
    get_quote_by_id,
    mark_quote_state,
    save_quote
)

logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------
# POST /quotes/pension
# ------------------------------------------------------
@router.post("/quotes/pension", response_model=PensionQuoteResponseModel)
async def post_pension_quote(
    request_model: PensionQuoteRequestModel,
    token_payload: dict = Depends(require_quote_write_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"【API】/api/v1/quotes/pension 呼び出し (user_id={user_id_from_token})")
    result = await calculate_quote(request_model, mongo_client, user_id_from_token)
    await save_quote(user_id_from_token, request_model, result)
    return result

# ------------------------------------------------------
# GET /my/quotes
# ------------------------------------------------------
@router.get("/my/quotes", response_model=List[PensionQuoteResponseModel])
async def get_my_quotes(
    token_payload: dict = Depends(require_quote_write_permission)
):
    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"【API】/api/v1/my/quotes 呼び出し (user_id={user_id_from_token})")
    return await get_quotes_by_user_id(user_id_from_token)

# ------------------------------------------------------
# GET /my/quotes/{quote_id}
# ------------------------------------------------------
@router.get("/my/quotes/{quote_id}", response_model=PensionQuoteResponseModel)
async def get_my_quote_by_id(
    quote_id: str = Path(..., description="取得対象の見積もりID"),
    token_payload: dict = Depends(require_quote_write_permission)
):
    logger.info(f"【API】/api/v1/my/quotes/{quote_id} 呼び出し")

    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    quote = await get_quote_by_id(quote_id)

    user_id_from_quote = quote.user_id
    logger.info(f"検索した見積もりを作成したユーザ (user_id={user_id_from_quote})")
    logger.info(f"トークンから取得したユーザID (user_id={user_id_from_token})")
    if user_id_from_quote != user_id_from_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他人の見積もりは参照できません")

    return quote

# ------------------------------------------------------
# PUT /my/quotes/{quote_id}/changestate
# ------------------------------------------------------
@router.put("/my/quotes/{quote_id}/changestate", response_model=PensionQuoteResponseModel)
async def update_my_quote_state(
    update_model: QuoteStateUpdateModel,
    quote_id: str = Path(..., description="更新対象の見積もりID"),
    token_payload: dict = Depends(require_quote_write_permission)
):
    logger.info(f"【API】/api/v1/my/quotes/{quote_id}/changestate 状態更新呼び出し")

    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    updated_quote = await mark_quote_state(quote_id, user_id_from_token, new_state=update_model.new_state)
    return updated_quote
