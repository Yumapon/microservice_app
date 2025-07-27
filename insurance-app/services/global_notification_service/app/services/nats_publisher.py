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
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from app.config.config import Config

config = Config()
logger = logging.getLogger(__name__)

# グローバル接続インスタンス（初期はNone）
nats_client: Optional[NATS] = None

async def init_nats_connection():
    """
    アプリ起動時に呼び出される NATS 接続初期化関数
    """
    global nats_client
    if nats_client is None:
        logger.info("NATS接続を初期化: %s", config.nats["address"])
        nats_client = NATS()
        await nats_client.connect(config.nats["address"])
        logger.info("NATS接続完了")

async def close_nats_connection():
    """
    アプリ終了時に呼び出される NATS 切断処理
    """
    global nats_client
    if nats_client and nats_client.is_connected:
        await nats_client.close()
        logger.info("NATS接続をクローズしました")

logger = logging.getLogger(__name__)

async def publish_event(subject: str, payload: dict):
    """
    再利用中のNATS接続を用いて、指定トピックにイベントを送信する

    Parameters:
        subject (str): トピック名（例: "applications.ApplicationConfirmed"）
        payload (dict): JSON形式のペイロード
    """
    if not nats_client or not nats_client.is_connected:
        raise RuntimeError("NATS接続が確立されていません")

    try:
        message = json.dumps(payload, ensure_ascii=False, default=str).encode()
        logger.info("NATSパブリッシュ開始: subject=%s", subject)
        await nats_client.publish(subject, message)
        logger.info("NATSパブリッシュ成功: subject=%s", subject)
    except (ErrConnectionClosed, ErrTimeout, ErrNoServers) as e:
        logger.error("NATSパブリッシュ失敗: subject=%s, error=%s", subject, str(e))
        raise