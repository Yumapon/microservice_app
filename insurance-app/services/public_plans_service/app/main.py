from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pydantic_settings import BaseSettings  # こちらからimport
from typing import List
import logging
import uvicorn
import os
import sys
import time
from multiprocessing import current_process

# ログ設定
class JapanFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        jst = time.localtime(record.created + 9 * 3600)
        return time.strftime("%Y-%m-%d %H:%M:%S", jst)

formatter = JapanFormatter("[%(asctime)s] [%(process)d] %(levelname)s %(module)s %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger("plans")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# 環境設定
class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "insurance"

settings = Settings()

# DB接続
client = AsyncIOMotorClient(settings.mongodb_uri)
db = client[settings.mongodb_db]

# FastAPI初期化
app = FastAPI(title="Public Plans Service")

# モデル定義
class Plan(BaseModel):
    plan_id: str
    name: str
    description: str
    image_key: str

@app.get("/public/plans", response_model=List[Plan])
async def get_plans():
    logger.info("GET /public/plans called")
    plans_cursor = db.plans.find({})
    plans = []
    async for doc in plans_cursor:
        plans.append(Plan(
            plan_id=doc.get("plan_id"),
            name=doc.get("name"),
            description=doc.get("description"),
            image_key=doc.get("image_key")
        ))
    return plans

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
