# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.auth_guard import get_valid_session
from app.model.bff_quote_with_application import QuoteWithApplicationModel
from app.model.bff_dashboard import DashboardResponseModel
from app.model.bff_quotes_summary import QuoteSummaryResponseModel
from app.model.bff_contracts_summary import ContractSummaryResponseModel
from app.model.bff_homepage_info import HomepageInfoResponseModel

from app.services.bff_dashboard_service import fetch_user_dashboard
from app.services.bff_quotes_summary_service import fetch_quote_summary
from app.services.bff_contracts_summary_service import fetch_contract_summary
from app.services.bff_homepage_info_service import fetch_homepage_info
from app.services.bff_quotes_with_application_service import fetch_quotes_with_application

from app.config.config import Config

# ------------------------------------------------------------------------------
# 初期設定
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
router = APIRouter()
config = Config()

# ------------------------------------------------------------------------------
# 未認証ユーザー向けBFF
# ------------------------------------------------------------------------------
@router.get("/public/homepage-info", response_model=HomepageInfoResponseModel)
async def get_homepage_info():
    """
    非ログイン時トップ画面に表示する情報（保険紹介、キャンペーン）を取得
    """
    logger.info("[GET] /bff/public/homepage-info called")
    try:
        return await fetch_homepage_info()
    except Exception as e:
        logger.exception("ホームページ情報取得失敗")
        raise HTTPException(status_code=500, detail="ホームページ情報の取得に失敗しました")

# ------------------------------------------------------------------------------
# 認証済みユーザー向けBFF
# ------------------------------------------------------------------------------
@router.get("/my/quotes-with-application", response_model=List[QuoteWithApplicationModel])
async def get_quotes_with_application(user_session: dict = Depends(get_valid_session)):
    """
    見積もり情報に申込情報を合成して返すエンドポイント。
    - 申込があれば application フィールドに含める。
    - UI向けに最適化された構造。
    """
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[BFF] ユーザー {user_id} の見積+申込一覧取得処理開始")
    try:
        response_data = await fetch_quotes_with_application(access_token=access_token)
        logger.debug(f"[BFF] 合成結果件数: {len(response_data)}")
        return response_data
    except Exception as e:
        logger.exception("[BFF] 合成処理中にエラー発生")
        raise HTTPException(status_code=500, detail="見積・申込情報の取得に失敗しました")

@router.get("/my/dashboard", response_model=DashboardResponseModel)
async def get_user_dashboard(user_session: dict = Depends(get_valid_session)):
    """
    ログインユーザー向けダッシュボード情報を返却
    - 見積もり一覧
    - 申込中ステータス
    - 契約一覧
    - 未読通知数（仮）
    """
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]
    logger.info(f"[GET] /bff/my/dashboard by user_id={user_id}")
    try:
        response_data = await fetch_user_dashboard(access_token=access_token)
        logger.debug(f"Dashboard response: {response_data}")
        return response_data
    except Exception as e:
        logger.exception("ダッシュボード取得失敗")
        raise HTTPException(status_code=500, detail="ダッシュボード情報の取得に失敗しました")
    
@router.get("/my/quotes-summary", response_model=QuoteSummaryResponseModel)
async def get_quote_summary(user_session: dict = Depends(get_valid_session)):
    """
    ログインユーザーの見積もり状態を集約したサマリー情報を返す
    """
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]

    logger.info(f"[GET] /bff/my/quotes-summary called by user_id={user_id}")

    try:
        return await fetch_quote_summary(access_token=access_token)
    except Exception as e:
        logger.exception("見積もりサマリー取得失敗")
        raise HTTPException(status_code=500, detail="見積もりサマリーの取得に失敗しました")
    
@router.get("/my/contracts-summary", response_model=ContractSummaryResponseModel)
async def get_contract_summary(user_session: dict = Depends(get_valid_session)):
    """
    ログインユーザーの契約状態を集約したサマリー情報を返す
    """
    user_id = user_session["user_info"]["sub"]
    access_token = user_session["access_token"]

    logger.info(f"[GET] /bff/my/contracts-summary called by user_id={user_id}")

    try:
        return await fetch_contract_summary(access_token=access_token)
    except Exception as e:
        logger.exception("契約サマリー取得失敗")
        raise HTTPException(status_code=500, detail="契約サマリーの取得に失敗しました")