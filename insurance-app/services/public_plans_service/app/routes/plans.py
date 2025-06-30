# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from fastapi import APIRouter, Depends
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient

from app.dependencies.get_mongo_client import get_mongo_client
from app.models.plans import Plan
from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期化
# ------------------------------------------------------------------------------
config = Config()
logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------------------------------
# ルーティング定義
# ------------------------------------------------------------------------------
@router.get("/public/plans", response_model=List[Plan])
async def get_plans(
    db: AsyncIOMotorClient = Depends(get_mongo_client)
):
    logger.info("【API】/public/plans 呼び出し")
    collection = db.get_database(config.mongodb["database"]).get_collection(config.mongodb["collection"])
    plans = []
    async for doc in collection.find():
        plans.append(Plan(
            plan_id=doc.get("plan_id"),
            name=doc.get("name"),
            description=doc.get("description"),
            image_key=doc.get("image_key")
        ))
    return plans