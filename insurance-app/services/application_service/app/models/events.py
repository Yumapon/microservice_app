# -*- coding: utf-8 -*-
"""
NATS経由で受信・送信する保険申込関連イベントのPydanticモデル定義

- ApplicationConfirmedEvent:
    保険申込が確定されたことを通知するイベント
- ApplicationCancelledEvent:
    保険申込がキャンセルされたことを通知するイベント

これらのイベントは application_service から quotation_service に向けて送信され、
quotation_service 側では該当 quote_id に対して状態（quote_state）を更新する役割を持つ。
"""

from pydantic import BaseModel, Field
from datetime import datetime

# ------------------------------------------------------------------------------
# ApplicationConfirmed イベントモデル
# ------------------------------------------------------------------------------
class ApplicationConfirmedEvent(BaseModel):
    """
    保険申込が確定したことを示すイベントモデル

    - application_service → quotation_service に対して送信
    - quotation_service はこれを受信し、該当 quote_id の状態を "applied" に変更する
    """
    event: str = Field(..., description='イベント種別（固定値: "ApplicationConfirmed"）')
    quote_id: str = Field(..., description="対象の見積もりID（UUID）")
    user_id: str = Field(..., description="申込を行ったユーザーのID（UUID）")
    application_id: str = Field(..., description="確定された申込ID（UUID）")
    confirmed_at: datetime = Field(..., description="申込が確定された日時（ISO 8601形式）")

# ------------------------------------------------------------------------------
# ApplicationCancelled イベントモデル
# ------------------------------------------------------------------------------
class ApplicationCancelledEvent(BaseModel):
    """
    保険申込がキャンセルされたことを示すイベントモデル

    - application_service → quotation_service に対して送信
    - quotation_service はこれを受信し、該当 quote_id の状態を "cancelled" に変更する
    """
    event: str = Field(..., description='イベント種別（固定値: "ApplicationCancelled"）')
    quote_id: str = Field(..., description="対象の見積もりID（UUID）")
    user_id: str = Field(..., description="申込を行ったユーザーのID（UUID）")
    application_id: str = Field(..., description="キャンセルされた申込ID（UUID）")
    cancelled_at: datetime = Field(..., description="申込がキャンセルされた日時（ISO 8601形式）")
