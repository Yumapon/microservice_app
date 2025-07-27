# -*- coding: utf-8 -*-
"""
NATSイベント購読モジュール（quotation_service）

- "applications.*" トピックを購読し、保険申込関連イベント（例: ApplicationConfirmed, ApplicationCancelled）を受信
- 対象の quote_id に対応する quote_state を適切に更新する
"""

import json
import logging
from datetime import datetime

from app.dependencies.get_mongo_client import get_mongo_client

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

from app.models.events import (
    CreateGlobalNotificationEvent,
)
from app.models.notification import UserNotification

from app.services.user_notification_service import (
    post_user_notifications,
)

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
    - "notifications.*" トピックを購読
    - 受信メッセージを汎用 message_handler に委譲
    """
    logger.info("[NATS] サブスクライバ初期化開始")
    try:
        nc = NATS()
        logger.debug(f"[NATS] 接続先: {config.nats['address']}")
        await nc.connect(config.nats["address"])
        logger.info("[NATS] 接続成功")

        # メッセージハンドラをトピックにバインド（notifications.*）
        await nc.subscribe("notifications.*", cb=message_handler)
        logger.info("NATS購読開始: トピック = notifications.*")

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

        if event_type == "GlobalNotificationCreated":
            event = CreateGlobalNotificationEvent(**data)
            logger.debug(f"[NATS] CreateGlobalNotificationEvent イベントインスタンス生成: {event}")
            await handle_user_notification_created(event)

        else:
            logger.warning(f"[NATS] 未対応のイベント種別を受信: event={event_type}")

    except Exception as e:
        logger.exception("NATSメッセージ処理中にエラーが発生しました")

# ------------------------------------------------------------------------------
# イベント別処理関数群
# ------------------------------------------------------------------------------
async def handle_user_notification_created(
        event: CreateGlobalNotificationEvent,
    ):
    """
    CreateGlobalNotificationEvent イベントの処理
    - user_notifications サービスのグローバル通知作成
    """
    logger.info(f"[NATS] GlobalNotificationCreated 処理開始: message_id={event.global_notification.message_id}")
    try:
        #user_notificationの形に処理
        user_notification = UserNotification(
            message_id=event.global_notification.message_id,
            user_id="all_user",  # 固定で格納
            type=event.global_notification.type,
            title=event.global_notification.title.dict(),
            message_summary=event.global_notification.message_summary.dict(),
            message_detail=event.global_notification.message_detail.dict(),
            is_important=False,  # グローバル通知には重要フラグなし
            delivery_status="delivered",
            delivered_at=event.global_notification.announcement_date,
            created_at=event.global_notification.created_at or datetime.utcnow(),
            updated_at=event.global_notification.updated_at or datetime.utcnow()
        )

        await post_user_notifications(
            notification = user_notification,
            mongo_client = get_mongo_client()
        )
        
    except Exception as e:
        logger.exception(f"[NATS] GlobalNotificationCreated 処理失敗: message_id={event.global_notification.message_id}")