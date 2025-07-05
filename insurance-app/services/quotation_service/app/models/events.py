# -*- coding: utf-8 -*-
"""
NATS経由で受信する保険申込関連イベントのPydanticモデル定義
- QuoteCreated: 見積もり作成時のイベント
- ApplicationConfirmedEvent: 申込確定時のイベント
- ApplicationCancelledEvent: 申込キャンセル時のイベント
"""

from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal

# ------------------------------------------------------------------------------
# QuoteCreated イベントモデル
# ------------------------------------------------------------------------------
class QuoteCreatedEvent(BaseModel):
    """
    見積もりが新規作成されたことを通知するイベントモデル
    - ステータス変更履歴とは別
    - 非同期でシナリオ保存や集計用途に使う
    """
    event: Literal["QuoteCreated"] = "QuoteCreated"
    quote_id: UUID = Field(..., description="見積もりID")
    user_id: str = Field(..., description="ユーザーID")
    created_at: datetime = Field(..., description="見積もり作成日時（契約日または現在時刻）")

# ------------------------------------------------------------------------------
# QuoteStatusChanged イベントモデル
# ------------------------------------------------------------------------------
class QuoteStatusChangedEvent(BaseModel):
    """
    見積もり状態が変更されたことを通知するイベントモデル
    MongoDBに保存され、変更履歴として扱う
    """
    event: Literal["QuoteStatusChanged"] = "QuoteStatusChanged"
    quote_id: UUID = Field(..., description="対象の見積もりID")
    from_state: str = Field(..., description="変更前の状態")
    to_state: str = Field(..., description="変更後の状態")
    changed_at: datetime = Field(..., description="変更日時")

# ------------------------------------------------------------------------------
# QuoteChanged イベントモデル
# ------------------------------------------------------------------------------
class QuoteChangedEvent(BaseModel):
    """
    見積もり内容が変更されたことを通知するイベントモデル
    MongoDBに保存され、変更履歴として扱う
    """
    event: Literal["QuoteChanged"] = "QuoteChanged"
    quote_id: UUID = Field(..., description="対象の見積もりID")
    changed_at: datetime = Field(..., description="変更日時")

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
