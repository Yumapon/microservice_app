from datetime import datetime
import logging
from uuid import uuid4

from app.models.notification import GlobalNotification
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)

async def get_all_global_notifications(
    mongo_client: AsyncIOMotorClient,
) -> List[GlobalNotification]:
       
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["global_collection"]
        logger.info(f"GlobalNotifications取得開始 (DB={db_name}, Collection={collection_name})")

        cursor = mongo_client[db_name][collection_name].find()
        documents = await cursor.to_list(length=None)

        logger.info(f"GlobalNotifications取得成功 (DB={db_name}, Collection={collection_name})")

        scenarios = [GlobalNotification(**doc) for doc in documents]
        return scenarios

    except Exception as e:
        logger.error(f"GlobalNotifications取得失敗: {e}")
        return []
    
async def post_global_notifications(
    notification: GlobalNotification,
    mongo_client: AsyncIOMotorClient,
) -> GlobalNotification:
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["global_collection"]
        logger.info(f"GlobalNotifications作成開始 (DB={db_name}, Collection={collection_name})")

        doc = notification.dict()
        doc["message_id"] = str(uuid4())
        doc["created_at"] = datetime.utcnow()
        doc["updated_at"] = datetime.utcnow()

        await mongo_client[db_name][collection_name].insert_one(doc)

        return GlobalNotification(**doc)

    except Exception as e:
        logger.error(f"GlobalNotifications取得失敗: {e}")
        return None