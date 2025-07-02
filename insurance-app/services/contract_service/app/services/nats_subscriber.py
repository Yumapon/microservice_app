# -*- coding: utf-8 -*-
"""
NATS購読処理

- applications.ApplicationConfirmed を購読し、契約情報を作成
"""

import logging
import json
from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from app.models.events import ApplicationConfirmedEvent
from app.services.contract_manager import create_contract_by_application_id

logger = logging.getLogger(__name__)

async def run_nats_subscriber():
    """
    NATSに接続し、契約作成イベントを購読する
    """
    nc = NATS()
    await nc.connect("nats://localhost:4222")  # 接続先を環境変数で切り替えてもOK

    async def message_handler(msg: Msg):
        """
        applications.ApplicationConfirmed イベント受信時の処理
        """
        try:
            data = json.loads(msg.data.decode())
            event_type = data.get("event")

            if event_type == "ApplicationConfirmed":
                logger.info("[NATS] ApplicationConfirmedイベント受信: %s", data)
                event = ApplicationConfirmedEvent(**data)
                await create_contract_by_application_id(
                    application_id=event.application_id,
                    user_id=event.user_id
                )
                logger.info("[NATS] 契約作成完了: application_id=%s", event.application_id)

            else:
                logger.warning("[NATS] 未対応イベント種別: %s", event_type)

        except Exception as e:
            logger.exception("[NATS] イベント処理中にエラー: %s", str(e))

    await nc.subscribe("applications.ApplicationConfirmed", cb=message_handler)
    logger.info("[NATS] applications.ApplicationConfirmed を購読中")
