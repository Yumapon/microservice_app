# -*- coding: utf-8 -*-
"""
保険契約申込APIエンドポイント
"""

import logging
from fastapi import APIRouter, Depends, Path, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

from app.dependencies.auth import require_quote_write_permission
from app.dependencies.get_mongo_client import get_mongo_client
from app.services.application_manager import create_application, get_quote_from_quotation_service
from app.models.applications import ApplicationResponseModel
from app.logic.applications_check import validate_quote_before_application

logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------
# POST /applications/{quote_id}
# ------------------------------------------------------
@router.post("/applications/{quote_id}", response_model=ApplicationResponseModel)
async def post_application_from_quote(
    quote_id: str = Path(..., description="申し込み対象の見積もりID"),
    token_payload: dict = Depends(require_quote_write_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    """
    特定の見積もりIDに基づいて保険申込処理を実施する。
    """
    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"【API】/api/v1/applications/{quote_id} 呼び出し (user_id={user_id_from_token})")

    try:
        # Step 1: 見積もり情報を取得
        quote = await get_quote_from_quotation_service(
            quote_id=quote_id,
            access_token=token_payload["access_token"]
        )

        # Step 2: 整合性チェック（ユーザーID一致＋利率が最新）
        await validate_quote_before_application(user_id=user_id_from_token, quote=quote, mongo_client=mongo_client)

        # Step 3: 申込処理
        application_result = await create_application(
            user_id=user_id_from_token, 
            quote=quote, 
            access_token=token_payload["access_token"]
        )
        
        logger.info(f"申込完了: application_id={application_result.application_id}")
        return application_result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except httpx.HTTPStatusError as e:
        logger.error(f"quotation_service エラー: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="見積もり取得または更新エラー")

    except Exception as e:
        logger.exception("申込処理中に予期しないエラーが発生しました")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="申込処理エラー")
