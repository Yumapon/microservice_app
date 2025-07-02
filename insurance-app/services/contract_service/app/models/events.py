# -*- coding: utf-8 -*-
"""
NATS経由で受信する保険申込関連イベントのPydanticモデル定義
- ApplicationConfirmedEvent: 申込確定時のイベント（契約作成用）
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from pydantic import BaseModel, Field
from datetime import datetime

# ------------------------------------------------------------------------------
# ApplicationConfirmed イベントモデル（契約作成に使用）
# ------------------------------------------------------------------------------
class ApplicationConfirmedEvent(BaseModel):
    """
    保険申込が確定したことを示すイベントモデル。
    application_service から contract_service に対して送信される。

    このイベントを受信した contract_service は、
    対象の application_id に基づいて契約を新規作成する。
    """
    event: str = Field(..., description='イベント種別（固定値: "ApplicationConfirmed"）')
    quote_id: str = Field(..., description="対象の見積もりID（UUID）")
    user_id: str = Field(..., description="申込者のユーザーID（UUID）")
    application_id: str = Field(..., description="確定済みの申込ID（UUID）")
    confirmed_at: datetime = Field(..., description="申込が確定された日時（ISO 8601形式）")
