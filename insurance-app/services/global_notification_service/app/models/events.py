from pydantic import BaseModel
from typing import Literal

from app.models.notification import GlobalNotification

# ----------------------------------------
# 全体向け通知を作成したイベントモデル
# ----------------------------------------
class CreateGlobalNotificationEvent(BaseModel):
    event: Literal["GlobalNotificationCreated"] = "GlobalNotificationCreated"
    global_notification: GlobalNotification