import logging

from app.models.notification import (
    UserNotification,
    ReadNotificationResponse,
    MarkReadRequest,
)
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)

async def get_user_notifications(
    user_id: str,
    mongo_client: AsyncIOMotorClient,
) -> List[UserNotification]:
       
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["user_collection"]
        logger.info(f"UserNotifications取得開始 (DB={db_name}, Collection={collection_name})")

        cursor = mongo_client[db_name][collection_name].find({
            "user_id": {"$in": [user_id, "all_user"]}
        })
        documents = await cursor.to_list(length=None)

        logger.info(f"UserNotifications取得成功 (DB={db_name}, Collection={collection_name})")

        notifications = [UserNotification(**doc) for doc in documents]
        return notifications

    except Exception as e:
        logger.error(f"UserNotifications取得失敗: {e}")
        return []
    
async def post_user_notifications(
    notification: UserNotification,
    mongo_client: AsyncIOMotorClient,
) -> UserNotification:
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["user_collection"]
        logger.info(f"UserNotifications登録開始 (DB={db_name}, Collection={collection_name})")

        #登録
        await mongo_client[db_name][collection_name].insert_one(notification.dict())
        logger.info(f"UserNotifications登録完了 (DB={db_name}, Collection={collection_name})")
        
        return notification

    except Exception as e:
        logger.error(f"UserNotifications登録失敗: {e}")
    
async def delete_user_notifications(
    user_id: str,
    mongo_client: AsyncIOMotorClient,
):
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["user_collection"]
        logger.info(f"UserNotifications削除開始 (DB={db_name}, Collection={collection_name})")

        result = await mongo_client[db_name][collection_name].delete_many({"user_id": user_id})
        logger.info(f"UserNotifications削除成功: {result.deleted_count} 件削除")

    except Exception as e:
        logger.error(f"UserNotifications削除失敗: {e}")

async def get_user_notifications_as_read(
    user_id: str, 
    mongo_client: AsyncIOMotorClient,
) -> List[str]:
    
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["status_collection"]
        logger.info(f"UserStatus取得開始 (DB={db_name}, Collection={collection_name})")

        # ユーザーの既読データを取得（なければ空リスト）
        record = await mongo_client[db_name][collection_name].find_one({"user_id": user_id})
        logger.debug(f"record: ({record})")
        already_read_ids = record.get("read_message_ids", []) if record else []
        logger.debug(f"ユーザの閲覧したMessage IDは ({already_read_ids}) です")

        return already_read_ids
    
    except Exception as e:
        logger.error(f"UserNotifications検索失敗: {e}")
  
async def mark_user_notifications_as_read(
    request: MarkReadRequest,
    user_id: str, 
    mongo_client: AsyncIOMotorClient,
) -> ReadNotificationResponse:
    
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["status_collection"]
        logger.info(f"UserStatus取得開始 (DB={db_name}, Collection={collection_name})")

        # ユーザーの既読データを取得（なければ空リスト）
        record = await mongo_client[db_name][collection_name].find_one({"user_id": user_id})
        logger.debug(f"record: ({record})")
        already_read_ids = record.get("read_message_ids", []) if record else []
        logger.info(f"ユーザの閲覧したMessage IDは ({already_read_ids}) です")

        # 今回の message_ids から新規に追加すべきものを抽出
        newly_marked = list(set(request.message_ids) - set(already_read_ids))

        if record:
            # 既存レコードに新規分を追記
            await mongo_client[db_name][collection_name].update_one(
                {"user_id": user_id},
                {"$addToSet": {"read_message_ids": {"$each": newly_marked}}}
            )
        else:
            # 新規レコードを作成
            await mongo_client[db_name][collection_name].insert_one({
                "user_id": user_id,
                "read_message_ids": newly_marked
            })

        return ReadNotificationResponse(
            user_id = user_id,
            updated_message_ids = request.message_ids,
            already_read_ids = already_read_ids,
            newly_marked_read = newly_marked
        )
    
    except Exception as e:
        logger.error(f"UserNotifications既読更新失敗: {e}")
    
async def delete_user_notifications_as_read(
    user_id: str,
    mongo_client: AsyncIOMotorClient,
):
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["status_collection"]
        logger.info(f"UserStatus削除開始 (DB={db_name}, Collection={collection_name})")

        # ユーザーの既読データを削除
        await mongo_client[db_name][collection_name].delete_one({"user_id": user_id})

        logger.info(f"UserStatus削除成功 (user_id={user_id})")
        return {"message": "User notifications deleted successfully."}

    except Exception as e:
        logger.error(f"UserStatus削除失敗: {e}")