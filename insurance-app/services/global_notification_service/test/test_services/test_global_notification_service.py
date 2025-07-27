import pytest
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import Config
from app.models.notification import GlobalNotification
from app.services.global_notification_service import (
    post_global_notifications,
    get_all_global_notifications,
)

config = Config()
DB_NAME = config.mongodb["database"]
COLLECTION_NAME = config.mongodb["global_collection"]


@pytest.mark.asyncio
async def test_post_global_notification_and_fetch(mongo_client: AsyncIOMotorClient):
    # --- データ削除 ---
    await mongo_client[DB_NAME][COLLECTION_NAME].delete_many({})

    # --- 登録データ（フィールドは全て自前で用意） ---
    sample_data = {
        "type": "info",
        "title": {"ja": "メンテナンス", "en": "Maintenance"},
        "message_summary": {"ja": "メンテ概要", "en": "Summary of maintenance"},
        "message_detail": {"ja": "詳細な説明", "en": "Detailed explanation"},
        "announcement_date": datetime(2025, 7, 1),
        "message_id": "temp-id",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    # --- 登録 ---
    inserted = await post_global_notifications(GlobalNotification(**sample_data), mongo_client)

    # --- 登録結果の検証（dictではなく属性でアクセス） ---
    assert inserted.message_id is not None
    assert inserted.title.ja == "メンテナンス"
    assert inserted.message_summary.en == "Summary of maintenance"
    assert isinstance(inserted.created_at, datetime)

    # --- 取得検証 ---
    result = await get_all_global_notifications(mongo_client)

    assert len(result) == 1
    fetched = result[0]
    assert fetched.title.en == "Maintenance"
    assert fetched.message_detail.ja == "詳細な説明"
    assert isinstance(fetched.announcement_date, datetime)