# -*- coding: utf-8 -*-
"""
申込前に見積もりの整合性（利率など）をチェックするロジック
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

from app.services.rate_loader import load_interest_rates

logger = logging.getLogger(__name__)

async def validate_quote_before_application(
    user_id: str,
    quote: dict,
    mongo_client: AsyncIOMotorClient
):
    """
    申込前に見積もりとMongoDBの利率情報が一致しているかチェック

    Parameters:
        user_id (str): ログインユーザーID
        quote (dict): quotation_serviceから取得した見積もりデータ
        mongo_client (AsyncIOMotorClient): MongoDBクライアント

    Raises:
        ValueError: 整合性が取れない場合（利率がずれている等）
    """
    logger.info("申込前の利率整合性チェック開始: user_id=%s, quote_id=%s", user_id, quote.get("quote_id"))

    # ユーザーの見積もりかどうかチェック
    logger.info(f"quote={quote}")
    user_id_from_quote = quote.get("user_id")
    logger.info(f"検索した見積もりを作成したユーザ (user_id={user_id})")
    logger.info(f"見積もりから取得したユーザID (user_id={user_id_from_quote})")
    if quote.get("user_id") != user_id:
        raise ValueError("他人の見積もりを利用することはできません")

    #見積もりの利率を取得(予定利率)
    quote_interest_rate = quote.get("contract_interest_rate")
    logger.info(f"quote_interest_rate={quote_interest_rate}")
    if quote_interest_rate is None:
        raise ValueError("見積もりに利率情報が含まれていません")

    #見積もりの契約日を取得
    # 引数 quote["contract_date"] が文字列なら datetime に変換してUTCに
    quote_contract_date_str = quote.get("contract_date")
    if isinstance(quote_contract_date_str, str):
        quote_contract_date = datetime.fromisoformat(quote_contract_date_str).replace(tzinfo=timezone.utc)
    else:
        quote_contract_date = quote_contract_date_str  # 既にdatetime型ならそのまま
    
    logger.info(f"quote_contract_date={quote_contract_date}")
    if quote_contract_date is None:
        raise ValueError("見積もりに契約開始日が含まれていません")
    
    # 利率情報をMongoDBから取得
    rates = await load_interest_rates(mongo_client, quote_contract_date)
    interest_rate = rates.get("contract_rate")
    #min_rate = rates.get("min_rate")
    #logger.info("[利率取得済] interest_rate: %s min_rate: %s", interest_rate, min_rate)
    logger.info("[利率取得済] interest_rate: %s ", interest_rate)

    if rates is None:
        raise ValueError("最新の利率情報を取得できません")

    #if quote_interest_rate != interest_rate or quote_min_rate != min_rate:
    #    raise ValueError(f"利率が最新ではありません quote_interest_rate: {quote_interest_rate} quote_min_rate: {quote_min_rate} interest_rate: {interest_rate} min_rate: {min_rate}")
    if quote_interest_rate != interest_rate:
        raise ValueError(f"利率が最新ではありません quote_interest_rate: {quote_interest_rate} interest_rate: {interest_rate}")