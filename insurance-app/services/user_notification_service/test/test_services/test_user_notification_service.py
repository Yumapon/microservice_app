import pytest
from bson import ObjectId
from datetime import datetime
from app.services.user_notification_service import (
    get_user_notifications,
    delete_user_notifications,
    get_user_notifications_as_read,
    mark_user_notifications_as_read,
    delete_user_notifications_as_read,
)
from app.models.notification import MarkReadRequest
from app.config.config import Config

config = Config()
DB_NAME = config.mongodb["database"]
USER_COLLECTION = config.mongodb["user_collection"]
STATUS_COLLECTION = config.mongodb["status_collection"]

@pytest.mark.asyncio
async def test_get_user_notifications(mongo_client):
    await mongo_client[DB_NAME][USER_COLLECTION].delete_many({"user_id": "test_user"})

    test_doc = {
        "_id": ObjectId(),
        "user_id": "test_user",
        "message_id": "msg-001",
        "type": "info",
        "title": {
            "ja": "タイトル",
            "en": "Title"
        },
        "message_summary": {
            "ja": "サマリー",
            "en": "Summary"
        },
        "message_detail": {
            "ja": "詳細",
            "en": "Detail"
        },
        "announcement_date": datetime(2025, 7, 1),
        "delivered_at": datetime(2025, 7, 2),
        "created_at": datetime(2025, 7, 1),
        "updated_at": datetime(2025, 7, 2)
    }

    collection = mongo_client[DB_NAME][USER_COLLECTION]
    await collection.insert_one(test_doc)

    result = await get_user_notifications("test_user", mongo_client)

    assert len(result) == 1
    assert result[0].message_id == "msg-001"

@pytest.mark.asyncio
async def test_delete_user_notifications(mongo_client):
    await mongo_client[DB_NAME][USER_COLLECTION].delete_many({"user_id": "delete_test"})

    test_docs = [
        {
            "user_id": "delete_test",
            "message_id": "a",
            "type": "info",
            "title": {"ja": "t", "en": "t"},
            "message_summary": {"ja": "s", "en": "s"},
            "message_detail": {"ja": "d", "en": "d"},
            "announcement_date": datetime(2025, 7, 1),
            "delivered_at": datetime(2025, 7, 2),
            "created_at": datetime(2025, 7, 1),
            "updated_at": datetime(2025, 7, 2)
        },
        {
            "user_id": "delete_test",
            "message_id": "b",
            "type": "info",
            "title": {"ja": "t", "en": "t"},
            "message_summary": {"ja": "s", "en": "s"},
            "message_detail": {"ja": "d", "en": "d"},
            "announcement_date": datetime(2025, 7, 1),
            "delivered_at": datetime(2025, 7, 2),
            "created_at": datetime(2025, 7, 1),
            "updated_at": datetime(2025, 7, 2)
        },
    ]

    collection = mongo_client[DB_NAME][USER_COLLECTION]
    await collection.insert_many(test_docs)

    await delete_user_notifications("delete_test", mongo_client)

    remaining = await collection.find({"user_id": "delete_test"}).to_list(length=None)
    assert len(remaining) == 0

@pytest.mark.asyncio
async def test_get_user_notifications_as_read_empty(mongo_client):
    await mongo_client[DB_NAME][STATUS_COLLECTION].delete_many({"user_id": "no_record"})

    read_ids = await get_user_notifications_as_read("no_record", mongo_client)
    assert read_ids == []

@pytest.mark.asyncio
async def test_mark_user_notifications_as_read_insert(mongo_client):
    await mongo_client[DB_NAME][STATUS_COLLECTION].delete_many({"user_id": "new_user"})

    request = MarkReadRequest(message_ids=["a", "b", "c"])
    response = await mark_user_notifications_as_read(request, "new_user", mongo_client)

    assert response.user_id == "new_user"
    assert set(response.updated_message_ids) == {"a", "b", "c"}
    assert response.already_read_ids == []
    assert set(response.newly_marked_read) == {"a", "b", "c"}

@pytest.mark.asyncio
async def test_mark_user_notifications_as_read_update(mongo_client):
    collection = mongo_client[DB_NAME][STATUS_COLLECTION]
    await collection.delete_many({"user_id": "existing_user"})

    await collection.insert_one({
        "user_id": "existing_user",
        "read_message_ids": ["x", "y"]
    })

    request = MarkReadRequest(message_ids=["x", "y", "z"])  # z は新規
    response = await mark_user_notifications_as_read(request, "existing_user", mongo_client)

    assert set(response.updated_message_ids) == {"x", "y", "z"}
    assert set(response.newly_marked_read) == {"z"}
    assert set(response.already_read_ids).issuperset({"x", "y"})

    doc = await collection.find_one({"user_id": "existing_user"})
    assert "z" in doc["read_message_ids"]

@pytest.mark.asyncio
async def test_delete_user_notifications_as_read(mongo_client):
    collection = mongo_client[DB_NAME][STATUS_COLLECTION]

    await collection.insert_one({
        "user_id": "delete_read",
        "read_message_ids": ["1", "2"]
    })

    result = await delete_user_notifications_as_read("delete_read", mongo_client)
    assert result["message"] == "User notifications deleted successfully."

    doc = await collection.find_one({"user_id": "delete_read"})
    assert doc is None