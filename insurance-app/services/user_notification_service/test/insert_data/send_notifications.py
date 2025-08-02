import requests
import random
import uuid
from datetime import datetime, timedelta
import json

# 固定ユーザーID
USER_ID = "c258480f-67f3-4fc9-b658-38d3bef862f6"

# POST先URL（${user_id} を埋め込み）
BASE_URL = f"http://localhost:8005/api/v1/user_notification/{USER_ID}"

# 通知タイプ一覧（少なくとも1つずつ含める）
NOTIFICATION_TYPES = ['info', 'warning', 'error', 'promotion', 'alert', 'progress']

# タイトル・メッセージのテンプレート（各通知タイプに応じて少し変える）
TITLES = {
    "ja": [
        "重要なお知らせ", "システム障害", "メンテナンス情報", "キャンペーン情報",
        "警告メッセージ", "進捗レポート"
    ],
    "en": [
        "Important Notice", "System Error", "Maintenance Info", "Campaign Info",
        "Warning Message", "Progress Report"
    ]
}

SUMMARIES = {
    "ja": [
        "システムのお知らせです。", "一部サービスに影響が発生しています。", "新しいキャンペーンが始まります。",
        "注意が必要なイベントがあります。", "サービスの状態に関する更新です。", "処理の進捗をご確認ください。"
    ],
    "en": [
        "This is a system notification.", "Some services are affected.", "New campaign is starting.",
        "Attention needed for an event.", "Update on service status.", "Please check the process status."
    ]
}

DETAILS = {
    "ja": "詳細はシステム管理者までお問い合わせください。",
    "en": "For more details, please contact system administrator."
}

def generate_notification(index: int, type_choice: str) -> dict:
    """通知データ1件分を生成する"""
    now = datetime.utcnow()
    created_at = now - timedelta(minutes=random.randint(1, 120))
    updated_at = created_at + timedelta(minutes=random.randint(1, 30))
    delivered_at = created_at + timedelta(minutes=random.randint(1, 10))

    return {
        "message_id": f"noti-{str(uuid.uuid4())[:8]}-{index}",
        "user_id": USER_ID,
        "type": type_choice,
        "title": {
            "ja": TITLES["ja"][NOTIFICATION_TYPES.index(type_choice)],
            "en": TITLES["en"][NOTIFICATION_TYPES.index(type_choice)]
        },
        "message_summary": {
            "ja": SUMMARIES["ja"][NOTIFICATION_TYPES.index(type_choice)],
            "en": SUMMARIES["en"][NOTIFICATION_TYPES.index(type_choice)]
        },
        "message_detail": {
            "ja": DETAILS["ja"],
            "en": DETAILS["en"]
        },
        "is_important": random.choice([True, False]),
        "delivery_status": "delivered",
        "delivered_at": delivered_at.isoformat() + "Z",
        "created_at": created_at.isoformat() + "Z",
        "updated_at": updated_at.isoformat() + "Z"
    }

def send_notifications():
    # 最初に全タイプを1つずつ入れる
    types_to_send = NOTIFICATION_TYPES.copy()

    # 残りの件数（20件中、残り）
    remaining = 20 - len(types_to_send)

    # 残りはランダムに選ぶ
    types_to_send += random.choices(NOTIFICATION_TYPES, k=remaining)

    random.shuffle(types_to_send)

    for i, notif_type in enumerate(types_to_send, 1):
        payload = generate_notification(i, notif_type)
        try:
            response = requests.post(BASE_URL, json=payload)
            print(f"[{i:02d}] status={response.status_code}, type={notif_type}")
        except Exception as e:
            print(f"[{i:02d}] エラー発生: {e}")

if __name__ == "__main__":
    send_notifications()