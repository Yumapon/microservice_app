# -*- coding: utf-8 -*-
"""
quotes, quote_details, quote_scenarios テーブルと連携するサービス層モジュール

- 見積もりの取得（一覧・個別）
- 見積もりの保存
- ステータス更新
"""

import logging
from typing import List
from uuid import UUID
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.db_models.quotes import Quote,QuoteDetail
from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    PensionQuoteScenarioModel,
    PensionQuoteCalculateResult
)

from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
config = Config()
rules = config.pension
logger = logging.getLogger(__name__)

####参照処理

# ------------------------------------------------------------------------------
# 見積もり一覧取得（ユーザー単位、Mongoなし）
# ------------------------------------------------------------------------------
async def get_quotes_by_user_id(
    session: AsyncSession,
    user_id: UUID
) -> List[PensionQuoteResponseModel]:
    """
    指定ユーザーの見積もりを最新順で取得（PostgreSQLのみ）

    Returns:
        List[PensionQuoteResponseModel]
    """
    logger.info("見積もり一覧取得: user_id=%s", user_id)

    # JOINして一括取得
    stmt = (
        select(Quote, QuoteDetail)
        .join(QuoteDetail, Quote.quote_id == QuoteDetail.quote_id)
        .where(Quote.user_id == user_id)
        .order_by(Quote.created_at.desc())
    )
    results = await session.execute(stmt)
    records = results.all()

    response_list = []
    for quote, detail in records:
        # MongoDBシナリオは含めないので空リスト
        response = _build_response_model(quote, detail, scenarios=[])
        response_list.append(response)

    return response_list

# ------------------------------------------------------------------------------
# 見積もり単体取得
# ------------------------------------------------------------------------------
async def get_quote_by_id(
        session: AsyncSession, 
        quote_id: UUID,
        user_id: UUID
) -> PensionQuoteResponseModel:
    """
    見積もりIDを指定して1件取得
    """
    logger.info("見積もり取得: quote_id=%s", quote_id)

    result = await session.execute(
        select(Quote, QuoteDetail)
        .join(QuoteDetail, Quote.quote_id == QuoteDetail.quote_id)
        .where(Quote.quote_id == quote_id)
    )
    record = result.first()
    if not record:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")
    
    quote, detail = record
    if str(quote.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="他人の見積もりは更新できません")

    logger.info(f"quote{quote}")
    response = _build_response_model(quote, detail, scenarios=[])
    return response
# ------------------------------------------------------------------------------
# 見積もりシナリオ一覧取得（見積もりID単位）
# ------------------------------------------------------------------------------
async def get_scenarios_by_quote_id(
    mongo_client: AsyncIOMotorClient,
    quote_id: str
) -> List[PensionQuoteScenarioModel]:
    """
    指定された quote_id に対応するシナリオ情報を MongoDB から取得する。

    :param mongo_client: MongoDBクライアントインスタンス
    :param quote_id: 見積もりID（UUID文字列）
    :return: PensionQuoteScenarioModel のリスト
    """
    try:
        db_name = config.mongodb["database"]
        collection_name = config.mongodb["scenario_collection"]
        logger.info(f"MongoDBシナリオ取得開始 (quote_id={quote_id})")

        cursor = mongo_client[db_name][collection_name].find({"quote_id": quote_id})
        documents = await cursor.to_list(length=None)

        logger.info(f"MongoDBシナリオ取得成功 (quote_id={quote_id}, 件数={len(documents)})")

        scenarios = [PensionQuoteScenarioModel(**doc) for doc in documents]
        return scenarios

    except Exception as e:
        logger.error(f"MongoDBシナリオ取得失敗 (quote_id={quote_id}): {e}")
        return []

####更新処理

# ------------------------------------------------------------------------------
# 見積もり保存処理（新規登録）
# ------------------------------------------------------------------------------
async def save_quote(
    session: AsyncSession,
    user_id: UUID,
    request: PensionQuoteRequestModel,
    calculate_result: PensionQuoteCalculateResult,
    operator_id: str = None
) -> UUID:
    """
    見積もりを quotes, quote_details に保存し、発行した quote_id を返す

    Parameters:
        session (AsyncSession): 非同期DBセッション
        user_id (UUID): ユーザーID
        request (PensionQuoteRequestModel): 入力内容（契約条件）
        response (PensionQuoteCalculateResult): 見積もり結果（契約日・金額・利率・控除など）

    Returns:
        UUID: 登録した見積もりの quote_id
    """
    logger.info("見積もり保存開始: quote_id=%s", calculate_result.quote_id)

    # quotes テーブル作成
    quote = Quote(
        quote_id=calculate_result.quote_id,
        user_id=user_id,
        quote_state="confirmed",
        created_by=operator_id or str(user_id),
        updated_by=operator_id or str(user_id),
    )

    # quote_details テーブル作成
    detail = QuoteDetail(
        quote_id=calculate_result.quote_id,
        plan_code=config.pension["plan_code"],
        birth_date=request.birth_date,
        gender=request.gender,
        monthly_premium=request.monthly_premium,
        payment_period_years=request.payment_period_years,
        tax_deduction_enabled=request.tax_deduction_enabled,
        pension_payment_years=request.pension_payment_years,
        contract_date=calculate_result.contract_date,
        contract_interest_rate=calculate_result.contract_interest_rate,
        total_paid_amount=calculate_result.total_paid_amount,
        pension_start_age=calculate_result.pension_start_age,
        annual_tax_deduction=calculate_result.annual_tax_deduction,
    )

    # 登録実行
    session.add_all([quote, detail])
    await session.commit()
    logger.info("見積もり保存完了: quote_id=%s", calculate_result.quote_id)

    return calculate_result.quote_id

# ------------------------------------------------------------------------------
# ステータス更新処理
# ------------------------------------------------------------------------------
async def mark_quote_state(
        session: AsyncSession, 
        quote_id: UUID, 
        user_id: UUID, 
        new_state: str
    ):
    """
    見積もりステータスを更新
    """
    logger.info("ステータス更新: quote_id=%s, new_state=%s", quote_id, new_state)

    result = await session.execute(
        select(Quote).where(Quote.quote_id == quote_id)
    )
    quote = result.scalar_one_or_none()

    if not quote:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")
    if str(quote.user_id) != str(user_id):
        raise HTTPException(status_code=403, detail="他人の見積もりは更新できません")

    quote.quote_state = new_state

    #Commit
    await session.commit()

    return

# ------------------------------------------------------------------------------
# 任意フィールド更新処理
# ------------------------------------------------------------------------------
async def update_quote(
    session: AsyncSession,
    quote_id: UUID,
    user_id: UUID,
    updates: PensionQuoteResponseModel
) -> PensionQuoteResponseModel:
    """
    見積もりの詳細情報（quote_details）を一部更新する

    Parameters:
    ----------
    session : AsyncSession
        SQLAlchemyの非同期セッション
    quote_id : UUID
        更新対象の見積もりID
    user_id : UUID
        リクエスト実行者のユーザーID（権限チェック用）
    updates : PensionQuoteResponseModel
        更新後の保険情報を格納したクラス

    Returns:
    -------
    PensionQuoteResponseModel
        更新後の見積もりレスポンスモデル
    """
    logger.info("見積もり更新開始: quote_id=%s, user_id=%s", quote_id, user_id)

    result = await session.execute(
        select(Quote, QuoteDetail)
        .join(QuoteDetail)
        .where(Quote.quote_id == quote_id)
    )
    record = result.first()

    if not record:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")

    quote, detail = record

    if quote.user_id != user_id:
        raise HTTPException(status_code=403, detail="他人の見積もりは更新できません")

    if quote.quote_state != "confirmed":
        raise HTTPException(status_code=400, detail="confirmed状態の見積もりのみ更新可能です")

    detail.contract_date = updates.contract_date
    detail.contract_interest_rate = updates.contract_interest_rate
    detail.total_paid_amount = updates.total_paid_amount
    detail.pension_start_age = updates.pension_start_age
    detail.annual_tax_deduction = updates.annual_tax_deduction
    detail.monthly_premium = updates.monthly_premium
    detail.payment_period_years = updates.payment_period_years
    detail.pension_payment_years = updates.pension_payment_years
    detail.tax_deduction_enabled = updates.tax_deduction_enabled

    await session.commit()

    return _build_response_model(quote, detail, scenarios=[])

# ------------------------------------------------------------------------------
# 見積もり削除
# ------------------------------------------------------------------------------

async def delete_quote(session: AsyncSession, quote_id: UUID, user_id: UUID):
    """
    見積もりを削除（子テーブルも CASCADE により削除）

    Raises:
        404: 存在しないquote_id
        403: 他ユーザーによる削除
    """
    logger.info("見積もり削除: quote_id=%s", quote_id)

    result = await session.execute(
        select(Quote).where(Quote.quote_id == quote_id)
    )
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(status_code=404, detail="見積もりが存在しません")
    if quote.user_id != user_id:
        raise HTTPException(status_code=403, detail="他人の見積もりは削除できません")

    #データ削除
    await session.delete(quote)
    #Commit
    await session.commit()
    logger.info("見積もり削除完了: quote_id=%s", quote_id)

# ------------------------------------------------------------------------------
# シナリオ保存関数（既存削除 → 上書き保存）
# ------------------------------------------------------------------------------
async def save_scenarios_to_mongo(
    mongo_client: AsyncIOMotorClient,
    quote_id: UUID,
    scenarios: List[PensionQuoteScenarioModel]
):
    """
    指定されたquote_idに紐づくシナリオ情報をMongoDBに上書き保存する。
    - 古いシナリオ情報はすべて削除され、新しいものに置き換えられる。
    - 各シナリオには quote_id と記録時刻（logged_at）を付与する。
    - 不正な形式（例: scenario_typeが複数のset）の場合は記録をスキップする。

    Parameters
    ----------
    mongo_client : AsyncIOMotorClient
        MongoDBの非同期クライアント
    quote_id : UUID
        上書き対象の見積もりID
    scenarios : List[PensionQuoteScenarioModel]
        上書き保存する新しいシナリオの一覧
    """
    logger.info("MongoDBシナリオ上書き開始: quote_id=%s", quote_id)

    # 保存先情報の取得
    db_name = config.mongodb["database"]
    collection_name = config.mongodb["scenario_collection"]
    collection = mongo_client[db_name][collection_name]

    # ① 既存のシナリオを一括削除
    delete_result = await collection.delete_many({"quote_id": str(quote_id)})
    logger.debug("既存シナリオ削除完了: 件数=%d", delete_result.deleted_count)

    # ② 新しいシナリオを構築・保存
    scenario_docs = []
    for scenario in scenarios:
        # Pydanticモデルを辞書形式に変換
        doc = scenario.dict()

        # MongoDB用のメタデータ追加
        doc["quote_id"] = str(quote_id)
        doc["logged_at"] = datetime.utcnow()

        # セット形式の異常値を検出し修正（過去の変換バグ対策）
        if isinstance(doc.get("scenario_type"), set):
            scenario_type_set = doc["scenario_type"]
            if len(scenario_type_set) == 1:
                doc["scenario_type"] = next(iter(scenario_type_set))
            else:
                logger.error("scenario_typeが不正（複数のset）: %s", scenario_type_set)
                continue  # このレコードはスキップ

        scenario_docs.append(doc)

    # ③ シナリオが存在する場合のみ保存
    if scenario_docs:
        await collection.insert_many(scenario_docs)
        logger.info("MongoDBシナリオ上書き完了: 件数=%d", len(scenario_docs))
    else:
        logger.warning("保存対象のシナリオが空のためMongoDBへの保存をスキップ")

# ------------------------------------------------------------------------------
# 内部: レスポンスモデル組み立て
# ------------------------------------------------------------------------------
def _build_response_model(
    quote: Quote,
    detail: QuoteDetail,
    scenarios: List[PensionQuoteScenarioModel]
) -> PensionQuoteResponseModel:
    """
    Quote + QuoteDetail + シナリオ情報を組み合わせてレスポンスモデルに変換
    """
    return PensionQuoteResponseModel(
        # --- quotesテーブル ---
        quote_id=quote.quote_id,
        user_id=quote.user_id,
        quote_state=quote.quote_state,
        created_at=quote.created_at,
        updated_at=quote.updated_at,
        created_by=quote.created_by,
        updated_by=quote.updated_by,

        # --- quote_detailsテーブル（契約条件） ---
        birth_date=detail.birth_date,
        gender=detail.gender,
        monthly_premium=detail.monthly_premium,
        payment_period_years=detail.payment_period_years,
        pension_payment_years=detail.pension_payment_years,
        tax_deduction_enabled=detail.tax_deduction_enabled,

        # --- quote_detailsテーブル（計算結果） ---
        contract_date=detail.contract_date,
        contract_interest_rate=float(detail.contract_interest_rate),
        total_paid_amount=detail.total_paid_amount,
        pension_start_age=detail.pension_start_age,
        annual_tax_deduction=detail.annual_tax_deduction,
        plan_code=detail.plan_code,

        # --- MongoDBシナリオ ---
        scenarios=scenarios
    )