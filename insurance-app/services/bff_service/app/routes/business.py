# -*- coding: utf-8 -*-
"""
トップ画面APIエンドポイント
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies.auth_guard import get_valid_session

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------------------------------
# 認証済みユーザー向けトップエンドポイント
# ------------------------------------------------------------------------------
@router.get("/top")
async def top(user_session: dict = Depends(get_valid_session)):
    """
    認証済みユーザーがアクセス可能なトップページ用API
    """
    logger.info("【API】/top 呼び出し（認証済み）")
    return JSONResponse(
        content={
            "message": "ようこそ！",
            "user": user_session["user_info"]
        }
    )