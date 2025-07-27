# scripts/seed_user_notifications.py

from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
import random

# MongoDB設定
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "notification_service"
COLLECTION_NAME = "user_notifications"

TYPES = ["info", "alert", "progress", "error", "warning", "promotion", "error"]
DELIVERY_STATUSES = ["delivered", "pending", "failed"]

# 1人分の固定ユーザーIDを生成（テスト用UUID）
user_ids = [str(uuid.uuid4()) for _ in range(2)]
user_ids.append("c258480f-67f3-4fc9-b658-38d3bef862f6")

# MongoDB接続
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

now = datetime.utcnow()
documents = []

for user_id in user_ids:
    for i in range(20):
        delta_days = random.randint(0, 30)
        doc = {
            "message_id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": random.choice(TYPES),
            "title": {
                "ja": f"{user_id} 宛通知タイトル {i + 1}",
                "en": f"Notification Title {i + 1} for {user_id[:6]}"
            },
            "message_summary": {
                "ja": f"{user_id} 宛通知 {i + 1} の概要",
                "en": f"Summary {i + 1} for {user_id[:6]}"
            },
            "message_detail": {
                "ja": f"{user_id} 宛通知 {i + 1} の詳細内容",
                "en": f"Detail {i + 1} for {user_id[:6]}"
            },
            "is_important": random.choice([True, False]),
            "delivery_status": random.choice(DELIVERY_STATUSES),
            "delivered_at": now - timedelta(days=delta_days, minutes=random.randint(1, 30)),
            "created_at": now - timedelta(days=delta_days, minutes=60),
            "updated_at": now - timedelta(days=delta_days, minutes=30),
        }
        documents.append(doc)

collection.insert_many(documents)
print(f"✅ 個人通知 {len(documents)} 件を挿入しました。ユーザー数: {len(user_ids)}")