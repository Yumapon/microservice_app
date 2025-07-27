# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
import httpx
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path
from fastapi.responses import JSONResponse

from app.model.bff_quotes import (
    PensionQuoteRequestModel,
    QuoteStateUpdateRequest,
    PartialQuoteUpdateModel,
)
from app.model.bff_applications import (
    PensionApplicationRequestModel,
    ApplicationStatusUpdateRequest,
    PartialApplicationUpdateModel
)
from app.dependencies.auth_guard import get_valid_session

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
router = APIRouter()
config = Config()

QUOTES_CREATE_URL = config.quotation_service["base_url"] + config.quotation_service["create_path"]
QUOTES_GET_URL = config.quotation_service["base_url"] + config.quotation_service["get_path"]
QUOTES_CHANGE_URL = config.quotation_service["base_url"] + config.quotation_service["change_path"]
QUOTES_CHANGE_STATUS_ADDITIONAL_PATH = config.quotation_service["change_status_additional_path"]

APPLICATIONS_CREATE_URL = config.application_service["base_url"] + config.application_service["create_path"]
APPLICATIONS_GET_URL = config.application_service["base_url"] + config.application_service["get_path"]
APPLICATIONS_CHANGE_URL = config.application_service["base_url"] + config.application_service["change_path"]
APPLICATIONS_CHANGE_STATUS_ADDITIONAL_PATH = config.application_service["change_status_additional_path"]

CONTRACTS_URL = config.contraction_service["base_url"] + config.contraction_service["get_path"]

# ------------------------------------------------------------------------------
# Quotation_service Proxy API
# ------------------------------------------------------------------------------
@router.post("/quotes/pension")
async def post_pension_quote(
    request_model: PensionQuoteRequestModel,
    user_session: dict = Depends(get_valid_session)
):
    """
    個人年金保険の見積もり作成処理（BFF経由で quotation_service を呼び出す）

    - 成功時は PensionQuoteResponseModel を返却
    """
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                QUOTES_CREATE_URL,
                headers=headers,
                content=request_model.json()
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 見積作成失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積もり作成APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 見積もり作成成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 見積作成処理中に例外発生")
        raise HTTPException(status_code=500, detail="見積もり作成処理に失敗しました")
    
@router.put("/my/quotes/{quote_id}/changestate")
async def update_quote_state(
    payload: QuoteStateUpdateRequest,
    quote_id: str = Path(..., description="更新対象の見積もりID"),
    user_session: dict = Depends(get_valid_session)
): 
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積ステータス更新処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                QUOTES_CHANGE_URL + "/" + quote_id + QUOTES_CHANGE_STATUS_ADDITIONAL_PATH,
                headers=headers,
                content=payload.json()
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 見積ステータス更新失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積ステータス更新APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 見積ステータス更新成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 見積ステータス更新処理中に例外発生")
        raise HTTPException(status_code=500, detail="見積ステータス更新処理に失敗しました")
    
@router.patch("/my/quotes/{quote_id}")
async def patch_my_quote(
    payload: PartialQuoteUpdateModel,
    quote_id: str = Path(..., description="対象の見積もりID"),
    user_session: dict = Depends(get_valid_session)
):
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積更新処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                QUOTES_CHANGE_URL + "/" + quote_id,
                headers=headers,
                content=payload.json()
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 見積更新失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積更新APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 見積更新成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 見積更新処理中に例外発生")
        raise HTTPException(status_code=500, detail="見積更新処理に失敗しました")
    
@router.delete("/my/quotes/{quote_id}")
async def update_quote_state(
    quote_id: str = Path(..., description="削除対象の見積もりID"),
    user_session: dict = Depends(get_valid_session)
):
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積削除処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                QUOTES_CHANGE_URL + "/" + quote_id,
                headers=headers
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 見積削除失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積削除APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 見積削除成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 見積削除処理中に例外発生")
        raise HTTPException(status_code=500, detail="見積削除処理に失敗しました")
    
@router.get("/my/quotes")
async def get_my_quotes(
    user_session: dict = Depends(get_valid_session)
):

    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積取得処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                QUOTES_GET_URL,
                headers=headers,
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 見積取得失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積もり取得APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 見積取得成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 見積取得処理中に例外発生")
        raise HTTPException(status_code=500, detail="見積取得処理に失敗しました")
    
@router.get("/my/quotes/{quote_id}")
async def get_my_quotes(
    quote_id: str = Path(..., description="取得対象の見積もりID"),
    user_session: dict = Depends(get_valid_session)
):

    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積取得処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                QUOTES_GET_URL + "/" + quote_id,
                headers=headers,
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 見積取得失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積もり取得APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 見積取得成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 見積取得処理中に例外発生")
        raise HTTPException(status_code=500, detail="見積取得処理に失敗しました")

# ------------------------------------------------------------------------------
# Application_service Proxy API
# ------------------------------------------------------------------------------
@router.post("/applications/pension")
async def post_application(
    request_model: PensionApplicationRequestModel,
    user_session: dict = Depends(get_valid_session)
):

    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の申込処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                APPLICATIONS_CREATE_URL,
                headers=headers,
                content=request_model.json()
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 申込失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="申込APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 申込成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 申込処理中に例外発生")
        raise HTTPException(status_code=500, detail="申込処理に失敗しました")
    
@router.put("/my/applications/{application_id}/changestate")
async def update_application_satus(
    payload: ApplicationStatusUpdateRequest,
    application_id: str = Path(..., description="更新対象の申込ID"),
    user_session: dict = Depends(get_valid_session)
):
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の申込ステータス更新処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                APPLICATIONS_CHANGE_URL + "/" + application_id + APPLICATIONS_CHANGE_STATUS_ADDITIONAL_PATH,
                headers=headers,
                content=payload.json()
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 申込ステータス更新失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="申込ステータス更新APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 申込ステータス更新成功 application_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 申込ステータス更新処理中に例外発生")
        raise HTTPException(status_code=500, detail="申込ステータス更新処理に失敗しました")
    
@router.patch("/my/applications/{application_id}")
async def patch_my_application(
    payload: PartialApplicationUpdateModel,
    application_id: str = Path(..., description="更新対象の申込ID"),
    user_session: dict = Depends(get_valid_session)
):
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の申込更新処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                APPLICATIONS_CHANGE_URL + "/" + application_id,
                headers=headers,
                content=payload.json()
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 見積更新失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="見積更新APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 見積更新成功 application_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 見積更新処理中に例外発生")
        raise HTTPException(status_code=500, detail="見積更新処理に失敗しました")
    
@router.delete("/my/applications/{application_id}")
async def delete_application_state(
    application_id: str = Path(..., description="更新対象の申込ID"),
    user_session: dict = Depends(get_valid_session)
):
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の申込キャンセル処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                APPLICATIONS_CHANGE_URL + "/" + application_id,
                headers=headers
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 申込キャンセル失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="申込キャンセルAPIの呼び出しに失敗しました")

        logger.info(f"[BFF] 申込キャンセル成功 application_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 申込キャンセル処理中に例外発生")
        raise HTTPException(status_code=500, detail="申込キャンセル処理に失敗しました")
    
@router.get("/my/applications")
async def get_my_applications(
    user_session: dict = Depends(get_valid_session)
):

    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の申込取得処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                APPLICATIONS_GET_URL,
                headers=headers,
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 申込取得失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="申込取得APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 申込取得成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 申込取得処理中に例外発生")
        raise HTTPException(status_code=500, detail="申込取得処理に失敗しました")
    
@router.get("/my/applications/{application_id}")
async def get_my_application_by_id(
    application_id: str = Path(..., description="取得対象の申込ID"),
    user_session: dict = Depends(get_valid_session)
):

    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積取得処理開始")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                APPLICATIONS_GET_URL + "/" + application_id,
                headers=headers,
            )

        if response.status_code != 200:
            logger.error(f"[BFF] 申込取得失敗: status={response.status_code}, body={response.text}")
            raise HTTPException(status_code=response.status_code, detail="申込取得APIの呼び出しに失敗しました")

        logger.info(f"[BFF] 申込取得成功 quote_id含む")
        return JSONResponse(content=response.json(), status_code=response.status_code)

    except Exception as e:
        logger.exception("[BFF] 申込取得処理中に例外発生")
        raise HTTPException(status_code=500, detail="申込取得処理に失敗しました")