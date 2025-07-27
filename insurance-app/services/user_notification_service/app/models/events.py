from typing import Literal
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ----------------------------------------
# 多言語メッセージ構造
# ----------------------------------------
class MultilingualMessage(BaseModel):
    ja: Optional[str]
    en: Optional[str]


# ----------------------------------------
# 全体向け通知モデル（DB用／レスポンス共通）
# ----------------------------------------
class GlobalNotification(BaseModel):
    message_id: str
    type: str = Field(..., description="通知タイプ（info, warning, error, promotion など）")
    title: MultilingualMessage
    message_summary: MultilingualMessage
    message_detail: MultilingualMessage
    announcement_date: datetime
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# ----------------------------------------
# 全体向け通知を作成したイベントモデル
# ----------------------------------------
class CreateGlobalNotificationEvent(BaseModel):
    event: Literal["GlobalNotificationCreated"] = "GlobalNotificationCreated"
    global_notification: GlobalNotification