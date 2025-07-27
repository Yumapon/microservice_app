from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
import random

# MongoDB設定
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "notification_service"
COLLECTION_NAME = "user_read_status"

# 同じユーザーID（10人分）
user_ids = [str(uuid.uuid4()) for _ in range(10)]

# 各ユーザーが既読にした通知ID（5〜15件の既読をランダムに作成）
documents = []

for user_id in user_ids:
    read_messages = []
    already_read_count = random.randint(5, 15)
    for _ in range(already_read_count):
        read_messages.append({
            "message_id": str(uuid.uuid4()),
            "read_at": datetime.utcnow() - timedelta(days=random.randint(0, 20), hours=random.randint(0, 23)),
        })

    read_message_ids = [msg["message_id"] for msg in read_messages]

    doc = {
        "user_id": user_id,
        "read_message_ids": read_message_ids,  # ✅ スキーマ必須
        "updated_at": datetime.utcnow()
    }
    documents.append(doc)

# MongoDBに接続して挿入
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

collection.insert_many(documents)
print(f"✅ 既読ステータスを {len(documents)} ユーザー分挿入しました。")