# -*- coding: utf-8 -*-
"""
保険契約申込APIエンドポイント

- 申込の作成
- 自ユーザーの申込一覧・詳細の取得
- 自ユーザーの申込キャンセル（ステータス更新）
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException, status

from app.dependencies.auth import require_application_write_permission, require_application_read_permission
from app.models.applications import (
    ApplicationRequestModel,
    ApplicationResponseModel,
    ApplicationStatusResponseModel
)
from app.services.application_manager import (
    create_application,
    get_applications_by_user_id,
    get_application_by_id,
    update_application_status
)

from motor.motor_asyncio import AsyncIOMotorClient
from app.dependencies.get_mongo_client import get_mongo_client
from app.logic.applications_check import validate_quote_before_application

logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------------------------------
# POST /applications
# ------------------------------------------------------------------------------
@router.post("/applications", response_model=ApplicationResponseModel)
async def post_application(
    request_model: ApplicationRequestModel,
    token_payload: dict = Depends(require_application_write_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    新規の保険申込を作成する（MongoDBの利率と整合性チェックを含む）

    Parameters:
        request_model (ApplicationRequestModel): 申込情報（見積もりデータ含む）
        token_payload (dict): Keycloakトークンから取得したユーザー情報
        mongo_client (AsyncIOMotorClient): MongoDBクライアント

    Returns:
        ApplicationResponseModel: 登録された申込情報

    Raises:
        HTTPException: 利率の不整合などで申込を拒否する場合
    """
    logger.info("【API】POST /applications 保険申込作成呼び出し")

    user_id_from_token = token_payload.get("sub")
    access_token = token_payload.get("access_token")
    quote_data = request_model.quote

    try:
        # 🔍 申込前にMongoDBの利率と整合性チェックを実施
        await validate_quote_before_application(
            user_id=user_id_from_token,
            quote=quote_data,
            mongo_client=mongo_client
        )
    except ValueError as e:
        logger.warning("申込前チェックに失敗: %s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # ✅ チェックOKなら申込実行
    return await create_application(user_id_from_token, quote_data, access_token, status="applied")


# ------------------------------------------------------------------------------
# GET /my/applications
# ------------------------------------------------------------------------------
@router.get("/my/applications", response_model=List[ApplicationResponseModel])
async def get_my_applications(
    token_payload: dict = Depends(require_application_read_permission),
):
    """
    自分の保険申込一覧を取得する

    Parameters:
        token_payload (dict): Keycloakトークンから取得したユーザー情報

    Returns:
        List[ApplicationResponseModel]: 自ユーザーの申込一覧
    """
    logger.info("【API】GET /my/applications 申込一覧取得呼び出し")
    user_id_from_token = token_payload.get("sub")
    return await get_applications_by_user_id(user_id_from_token)

# ------------------------------------------------------------------------------
# GET /my/applications/{application_id}
# ------------------------------------------------------------------------------
@router.get("/my/applications/{application_id}", response_model=ApplicationResponseModel)
async def get_my_application_by_id(
    application_id: str = Path(..., description="取得対象の申込ID"),
    token_payload: dict = Depends(require_application_read_permission),
):
    """
    自分の特定の保険申込情報を取得する

    Parameters:
        application_id (str): 対象申込ID
        token_payload (dict): Keycloakトークンから取得したユーザー情報

    Returns:
        ApplicationResponseModel: 指定IDの申込情報
    """
    logger.info("【API】GET /my/applications/%s 詳細取得呼び出し", application_id)
    user_id_from_token = token_payload.get("sub")
    return await get_application_by_id(application_id, user_id_from_token)

# ------------------------------------------------------------------------------
# PUT /my/applications/{application_id}/cancel
# ------------------------------------------------------------------------------
@router.put("/my/applications/{application_id}/cancel", response_model=ApplicationStatusResponseModel)
async def cancel_my_application(
    application_id: str = Path(..., description="キャンセル対象の申込ID"),
    token_payload: dict = Depends(require_application_write_permission),
):
    """
    自分の保険申込をキャンセルする（状態を 'cancelled' に更新）

    Parameters:
        application_id (str): 対象の申込ID
        token_payload (dict): Keycloakトークンから取得したユーザー情報

    Returns:
        ApplicationResponseModel: 更新後の申込情報
    """
    logger.info("【API】PUT /my/applications/%s/cancel キャンセル呼び出し", application_id)
    user_id_from_token = token_payload.get("sub")

    try:
        return await update_application_status(application_id, user_id_from_token, new_status="cancelled")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
