from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ----------------------------------------
# 共通の通知タイプ
# ----------------------------------------
class NotificationType(str):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    PROMOTION = "promotion"
    ALERT = "alert"
    PROGRESS = "progress"


# ----------------------------------------
# 多言語メッセージ構造
# ----------------------------------------
class MultilingualMessage(BaseModel):
    ja: Optional[str]
    en: Optional[str]

# ----------------------------------------
# 個人向け通知モデル
# ----------------------------------------
class UserNotification(BaseModel):
    message_id: str
    user_id: str
    type: str = Field(..., description="通知タイプ（info, alert, progress, errorなど）")
    title: MultilingualMessage
    message_summary: MultilingualMessage
    message_detail: MultilingualMessage
    is_important: Optional[bool] = False
    delivery_status: Optional[str] = "delivered"
    delivered_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

# ----------------------------------------
# 既読管理モデル（リスト形式）
# ----------------------------------------
class ReadNotificationResponse(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    updated_message_ids: List[str] = Field(..., description="処理対象となったすべてのmessage_id一覧")
    already_read_ids: List[str] = Field(..., description="すでに既読だったmessage_id一覧")
    newly_marked_read: List[str] = Field(..., description="今回新たに既読として記録されたmessage_id一覧")

    class Config:
        schema_extra = {
            "example": {
                "user_id": "abc123",
                "updated_message_ids": [
                    "uuid-1",
                    "uuid-2",
                    "uuid-3"
                ],
                "already_read_ids": [
                    "uuid-2"
                ],
                "newly_marked_read": [
                    "uuid-1",
                    "uuid-3"
                ]
            }
        }

# ----------------------------------------
# 既読管理モデル（リスト形式）
# ----------------------------------------
class MarkReadRequest(BaseModel):
    message_ids: List[str]
