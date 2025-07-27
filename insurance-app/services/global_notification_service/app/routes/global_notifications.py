import logging

from fastapi import APIRouter, Depends, Path, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.notification import GlobalNotification
from app.models.events import CreateGlobalNotificationEvent

from app.services.global_notification_service import (
    get_all_global_notifications,
    post_global_notifications
)
from app.dependencies.get_mongo_client import get_mongo_client

from app.services.nats_publisher import publish_event

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/global_notification", response_model=List[GlobalNotification])
async def fetch_global_notifications(
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    return await get_all_global_notifications(mongo_client=mongo_client)

@router.post("/global_notification", response_model=GlobalNotification)
async def create_global_notification(
    notification: GlobalNotification,
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
) -> GlobalNotification:
    """
    全体通知を作成する。
    """
    try:
        responce = await post_global_notifications(
            notification=notification,
            mongo_client=mongo_client
        )

        #イベントを発火
        event = CreateGlobalNotificationEvent(
            global_notification=responce,
        )
        await publish_event("notifications.GlobalNotificationCreated", event.dict())

        return responce

    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create global notification")