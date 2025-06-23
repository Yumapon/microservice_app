import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.dependencies.auth_guard import get_valid_session

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/top")
async def top(user_session: dict = Depends(get_valid_session)):
    logger.info("【API】/top 呼び出し（認証済み）")
    return JSONResponse(content={"message": "ようこそ！", "user": user_session["user_info"]})