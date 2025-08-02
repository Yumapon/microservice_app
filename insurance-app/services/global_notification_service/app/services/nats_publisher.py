# -*- coding: utf-8 -*-
"""
NATSイベントパブリッシュ処理モジュール（接続再利用対応）

- アプリ起動時に NATS へ接続
- publish_event() で常駐接続を使ってイベント送信
"""

import json
import logging
from typing import Optional
from nats.aio.client import Client as NATS

from app.config.config import Config

config = Config()
logger = logging.getLogger(__name__)

# グローバル接続インスタンス（初期はNone）
nats_client: Optional[NATS] = None

logger = logging.getLogger(__name__)

async def publish_event(subject: str, payload: dict):
    """
    再利用中のNATS接続を使ってイベント送信（再接続対応）
    """
    global nats_client
    if not nats_client or not nats_client.is_connected:
        try:
            logger.warning("NATS未接続。再接続を試みます...")
            nats_client = NATS()
            await nats_client.connect(
                servers=[config.nats["address"]],
                reconnect_time_wait=1,
                max_reconnect_attempts=2,
                connect_timeout=1
            )
            logger.info("NATS再接続成功")
        except Exception as e:
            logger.error("NATS再接続失敗（パブリッシュ中止）: %s", str(e))
            return  # ※失敗しても処理継続

    try:
        message = json.dumps(payload, ensure_ascii=False, default=str).encode()
        logger.info("NATSパブリッシュ開始: subject=%s", subject)
        await nats_client.publish(subject, message)
        logger.info("NATSパブリッシュ成功: subject=%s", subject)
    except Exception as e:
        logger.error("NATSパブリッシュ失敗: subject=%s, error=%s", subject, str(e))