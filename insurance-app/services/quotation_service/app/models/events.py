# -*- coding: utf-8 -*-
"""
NATS経由で受信する保険申込関連イベントのPydanticモデル定義
- ApplicationConfirmedEvent: 申込確定時のイベント
- ApplicationCancelledEvent: 申込キャンセル時のイベント
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from pydantic import BaseModel, Field
from datetime import datetime

# ------------------------------------------------------------------------------
# ApplicationConfirmed イベントモデル
# ------------------------------------------------------------------------------
class ApplicationConfirmedEvent(BaseModel):
    """
    保険申込が確定したことを示すイベントモデル
    application_service から quotation_service に対して送信される

    このイベントを受信した quotation_service は、
    対象の quote_id に紐づく quote_state を "applied" に更新する
    """
    event: str = Field(..., description='イベント種別（固定値: "ApplicationConfirmed"）')
    quote_id: str = Field(..., description="対象の見積もりID（UUID）")
    user_id: str = Field(..., description="申込者のユーザーID（UUID）")
    application_id: str = Field(..., description="確定済みの申込ID（UUID）")
    confirmed_at: datetime = Field(..., description="申込が確定された日時（ISO 8601形式）")

# ------------------------------------------------------------------------------
# ApplicationCancelled イベントモデル
# ------------------------------------------------------------------------------
class ApplicationCancelledEvent(BaseModel):
    """
    保険申込がキャンセルされたことを示すイベントモデル
    application_service から quotation_service に対して送信される

    このイベントを受信した quotation_service は、
    対象の quote_id に紐づく quote_state を "cancelled" に更新する
    """
    event: str = Field(..., description='イベント種別（固定値: "ApplicationCancelled"）')
    quote_id: str = Field(..., description="対象の見積もりID（UUID）")
    user_id: str = Field(..., description="申込者のユーザーID（UUID）")
    application_id: str = Field(..., description="キャンセル対象の申込ID（UUID）")
    cancelled_at: datetime = Field(..., description="申込がキャンセルされた日時（ISO 8601形式）")
