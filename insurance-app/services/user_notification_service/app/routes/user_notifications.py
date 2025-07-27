import logging

from fastapi import APIRouter, Depends, Path, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.notification import (
    UserNotification,
    ReadNotificationResponse,
    MarkReadRequest,
)
from app.services.user_notification_service import (
    get_user_notifications,
    post_user_notifications,
    delete_user_notifications,
    get_user_notifications_as_read,
    mark_user_notifications_as_read,
    delete_user_notifications_as_read,
)
from app.dependencies.get_mongo_client import get_mongo_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/user_notification/{user_id}", response_model=List[UserNotification])
async def fetch_user_notifications(
    user_id: str = Path(..., description="取得対象のユーザーID"),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    指定ユーザーの全通知を取得するエンドポイント。
    """
    return await get_user_notifications(
        user_id=user_id,
        mongo_client=mongo_client
    )

@router.post("/user_notification/{user_id}", response_model=UserNotification)
async def fetch_post_user_notifications(
    request: UserNotification,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    return await post_user_notifications(
        notification=request,
        mongo_client=mongo_client,
    )
    

@router.delete("/user_notification/{user_id}")
async def fetch_delete_user_notifications(
    user_id: str = Path(..., description="削除対象のユーザーID"),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    指定ユーザーの通知データを全削除するエンドポイント。
    """
    try:
        await delete_user_notifications(
            user_id=user_id,
            mongo_client=mongo_client
        )
        return {"message": "User notifications deleted successfully."}

    except Exception as e:
        logger.error(f"UserNotifications削除失敗: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user notifications")

@router.get("/user_notification/unread/{user_id}", response_model=List[UserNotification])
async def fetch_user_notifications_by_user_id(
    user_id: str = Path(..., description="取得対象のユーザーID"),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    指定ユーザーの未読通知のみを取得するエンドポイント。
    """
    try:
        # ユーザーの既読状態（message_id一覧）を取得
        already_read_ids = await get_user_notifications_as_read(
            user_id=user_id,
            mongo_client=mongo_client
        )

        # デバッグログ出力（既読ID）
        for id in already_read_ids:
            logger.debug(f"already_read_ids: ({id})")

        # 全通知を取得
        notifications = await get_user_notifications(
            user_id=user_id,
            mongo_client=mongo_client
        )

        # 未読通知のみを抽出
        unread_notifications = [
            notification for notification in notifications
            if notification.message_id not in already_read_ids
        ]

        return unread_notifications

    except Exception as e:
        logger.error(f"UserNotifications取得失敗: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user notifications")

@router.get("/user_notification/unread_count/{user_id}")
async def fetch_get_unread_count_by_user_id(
    user_id: str = Path(..., description="リセット対象のユーザーID"),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
) -> int:
    """
    指定ユーザーの未読通知件数を取得するエンドポイント。
    """
    try:
        # 既読通知IDの一覧を取得
        already_read_ids = await get_user_notifications_as_read(
            user_id=user_id,
            mongo_client=mongo_client
        )

        # 全通知の取得
        notifications = await get_user_notifications(
            user_id=user_id,
            mongo_client=mongo_client
        )

        # 未読件数をカウント
        unread_count = sum(
            1 for notification in notifications
            if notification.message_id not in already_read_ids
        )

        return unread_count

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch unread count")


@router.delete("/user_notification/reset/{user_id}")
async def fetch_reset_user_notifications(
    user_id: str = Path(..., description="リセット対象のユーザーID"),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    指定ユーザーの既読状態（user_status）をリセットするエンドポイント。
    """
    try:
        # 指定ユーザーの既読履歴を削除
        await delete_user_notifications_as_read(
            user_id=user_id,
            mongo_client=mongo_client
        )

        return {"message": "User notifications deleted successfully."}

    except Exception as e:
        logger.error(f"UserStatus削除失敗: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user notifications")


@router.get("/user_notification/read/{user_id}")
async def fetch_mark_user_notifications_as_read(
    user_id: str = Path(..., description="検索対象のID"),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    指定ユーザーの既読通知（message_id一覧）を取得するエンドポイント。
    """
    return await get_user_notifications_as_read(
        user_id=user_id,
        mongo_client=mongo_client,
    )

@router.post("/user_notification/read/{user_id}", response_model=ReadNotificationResponse)
async def fetch_mark_user_notifications_as_read(
    user_id: str = Path(..., description="更新対象のID"),
    request: MarkReadRequest = ...,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    指定ユーザーに対して、指定された通知を既読としてマークするエンドポイント。
    """
    return await mark_user_notifications_as_read(
        request=request,
        user_id=user_id,
        mongo_client=mongo_client,
    )