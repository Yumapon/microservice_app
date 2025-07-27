# -*- coding: utf-8 -*-
"""
NATSイベント購読モジュール（quotation_service）

- "applications.*" トピックを購読し、保険申込関連イベント（例: ApplicationConfirmed, ApplicationCancelled）を受信
- 対象の quote_id に対応する quote_state を適切に更新する
"""

import json
import logging
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

from app.models.events import (
    ApplicationCreatedEvent,
    ApplicationStatusChangedEvent,
    ApplicationChangedEvent,
)
from app.services.contract_manager import create_contract

from app.db.database import get_async_session

from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# NATS購読処理のエントリポイント
# ------------------------------------------------------------------------------
async def run_nats_subscriber():
    """
    quotation_service 起動時に呼び出されるNATS購読セットアップ関数。

    - NATSサーバに接続
    - "applications.*" トピックを購読
    - 受信メッセージを汎用 message_handler に委譲
    """
    logger.info("[NATS] サブスクライバ初期化開始")
    try:
        nc = NATS()
        logger.debug(f"[NATS] 接続先: {config.nats['address']}")
        await nc.connect(config.nats["address"])
        logger.info("[NATS] 接続成功")

        # メッセージハンドラをトピックにバインド（applications.*）
        await nc.subscribe("applications.*", cb=message_handler)
        logger.info("NATS購読開始: トピック = applications.*")
        
    except Exception as e:
        logger.exception("[NATS] サブスクライバ初期化中にエラーが発生しました")

# ------------------------------------------------------------------------------
# NATSメッセージ共通ハンドラ
# ------------------------------------------------------------------------------
async def message_handler(msg: Msg):
    """
    NATSから受信したメッセージを処理する共通ハンドラ。

    - JSONデコード → イベント種別判定 → 各処理にディスパッチ
    - サポート対象外のイベントは警告ログ出力
    - 処理中の例外はすべてログ出力し握り潰す（サービス継続性確保のため）
    """
    try:
        logger.debug(f"[NATS] メッセージ受信: subject={msg.subject}, data={msg.data}")
        data = json.loads(msg.data.decode())
        event_type = data.get("event")
        logger.debug(f"[NATS] パース結果: event_type={event_type}")

        if event_type == "ApplicationCreated":
            event = ApplicationCreatedEvent(**data)
            logger.debug(f"[NATS] ApplicationCreated イベントインスタンス生成: {event}")
            await handle_application_created(event)

        elif event_type == "ApplicationStatusChanged":
            event = ApplicationStatusChangedEvent(**data)
            logger.debug(f"[NATS] ApplicationStatusChanged イベントインスタンス生成: {event}")
            await handle_application_status_changed(event)

        elif event_type == "ApplicationChanged":
            event = ApplicationChangedEvent(**data)
            logger.debug(f"[NATS] ApplicationChanged イベントインスタンス生成: {event}")
            await handle_application_changed(event)

        else:
            logger.warning(f"[NATS] 未対応のイベント種別を受信: event={event_type}")

    except Exception as e:
        logger.exception("NATSメッセージ処理中にエラーが発生しました")

# ------------------------------------------------------------------------------
# イベント別処理関数群
# ------------------------------------------------------------------------------
async def handle_application_created(event: ApplicationCreatedEvent):
    """
    ApplicationCreated イベントの処理
    - quote_state を "applied" に変更
    """
    logger.info(f"[NATS] ApplicationCreated 処理開始: quote_id={event.quote_id}")

async def handle_application_status_changed(event: ApplicationStatusChangedEvent):
    """
    ApplicationStatusChanged イベントの処理

    - 保険申込の状態が変更されたことを示すイベント
    - 対象の quote_id に対して quote_state を更新
    """
    logger.info(f"[NATS] ApplicationStatusChanged 処理開始: quote_id={event.quote_id}")

    if event.to_state == "confirmed":
        try:
            async for session in get_async_session():
                await create_contract(
                    session=session,
                    application_id=event.application_id,
                )
                logger.info(f"[NATS] quote_state を 'applied' に更新完了: quote_id={event.quote_id}")
                break
        except Exception as e:
            logger.exception(f"[NATS] ApplicationCreated 処理失敗: quote_id={event.quote_id}")

async def handle_application_changed(event: ApplicationChangedEvent):
    """
    ApplicationChanged イベントの処理

    - 保険申込の内容が変更されたことを示すイベント
    """
    logger.info(f"[NATS] ApplicationChanged 処理開始: quote_id={event.quote_id}")