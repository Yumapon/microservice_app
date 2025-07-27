# -*- coding: utf-8 -*-
"""
全体通知のテストデータをMongoDBに50件挿入するスクリプト
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
import random

# MongoDB接続設定（適宜修正）
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "notification_service"
COLLECTION_NAME = "global_notifications"

# 通知タイプ候補
TYPES = ["info", "warning", "error", "promotion"]

# 接続
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# データ作成＆挿入
now = datetime.utcnow()
documents = []

for i in range(50):
    delta_days = random.randint(0, 30)
    doc = {
        "message_id": str(uuid.uuid4()),
        "type": random.choice(TYPES),
        "title": {
            "ja": f"通知タイトル {i + 1}",
            "en": f"Notification Title {i + 1}"
        },
        "message_summary": {
            "ja": f"これはテスト通知 {i + 1} の概要です。",
            "en": f"This is the summary of test notification {i + 1}."
        },
        "message_detail": {
            "ja": f"これはテスト通知 {i + 1} の詳細内容です。",
            "en": f"This is the detailed content of test notification {i + 1}."
        },
        "announcement_date": now - timedelta(days=delta_days),
        "created_at": now - timedelta(days=delta_days, seconds=60),
        "updated_at": now - timedelta(days=delta_days, seconds=30),
    }
    documents.append(doc)

# 挿入
collection.insert_many(documents)
print(f"✅ 全体通知 {len(documents)} 件を挿入しました。")