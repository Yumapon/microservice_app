# -*- coding: utf-8 -*-
"""
個人年金保険の見積もりAPIエンドポイント
"""

import logging
from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Path, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import require_quote_write_permission
from app.dependencies.get_mongo_client import get_mongo_client
from app.models.quotes import (
    PensionQuoteRequestModel,
    PensionQuoteResponseModel,
    QuoteStateUpdateModel,
    QuoteStateUpdateRequest, 
    QuoteState,
    PartialQuoteUpdateModel,
)
from app.db.database import get_async_session
from app.models.events import (
    QuoteCreatedEvent,
    QuoteStatusChangedEvent
)
from app.services.calculate_quote import calculate_quote
from app.services.quote_manager import (
    get_quotes_by_user_id,
    get_quote_by_id,
    mark_quote_state,
    save_quote,
    get_scenarios_by_quote_id,
    update_quote,
    save_scenarios_to_mongo
)

from app.services.nats_publisher import publish_event

logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------------------------------
# POST /quotes/pension - 新しい見積もりを作成
# ------------------------------------------------------------------------------
@router.post("/quotes/pension", response_model=PensionQuoteResponseModel)
async def post_pension_quote(
    request_model: PensionQuoteRequestModel,
    token_payload: dict = Depends(require_quote_write_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    session: AsyncSession = Depends(get_async_session),
):
    user_id = token_payload.get("sub")
    
    logger.info(f"[API] POST /quotes/pension called (user_id={user_id})")

    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    #見積もりを作成
    calculated_result = await calculate_quote(request_model, mongo_client)
    logger.debug(f"[DEBUG] calculated_result: {calculated_result}")

    #見積もりを格納
    quote_id = await save_quote(
        session=session,
        user_id=user_id,
        request=request_model,
        calculate_result=calculated_result
    )

    #シナリオを格納
    try:
        await save_scenarios_to_mongo(
            mongo_client=mongo_client,
            quote_id=str(quote_id),
            scenarios=calculated_result.scenarios
        )
    except Exception as e:
        logger.error("MongoDBシナリオ保存失敗: %s", e)
        raise HTTPException(status_code=500, detail="Failed to save scenario")

    #イベントを発火
    event = QuoteCreatedEvent(
        quote_id=quote_id,
        user_id=user_id,
        created_at=datetime.utcnow()
    )
    await publish_event("quotes.QuoteCreated", event.dict())

    #DBから最新データを取得してレスポンス構築
    created_quote = await get_quote_by_id(
        session=session,
        quote_id=quote_id,
        user_id=UUID(user_id)
    )
    created_quote.scenarios = calculated_result.scenarios

    return created_quote

# ------------------------------------------------------------------------------
# PUT /my/quotes/{quote_id}/changestate - 見積もり状態の更新
# ------------------------------------------------------------------------------

#状態遷移の定義
ALLOWED_TRANSITIONS = {
    QuoteState.confirmed: [QuoteState.applied, QuoteState.cancelled, QuoteState.expired],
    QuoteState.applied: [QuoteState.cancelled],
}

@router.put("/my/quotes/{quote_id}/changestate", response_model=QuoteStateUpdateModel)
async def update_quote_state(
    payload: QuoteStateUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
    quote_id: UUID = Path(..., description="更新対象の見積もりID"),
    token_payload: dict = Depends(require_quote_write_permission),
):
    user_id = token_payload.get("sub")
    logger.info(f"[API] PUT /my/quotes/{quote_id}/changestate 状態変更 (new_state={payload.new_state})")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    #変更前の状態を取得
    quote = await get_quote_by_id(session, quote_id, user_id)
    if not quote:
        raise HTTPException(status_code=404, detail="見積もりが見つかりません")
    current_state = QuoteState(quote.quote_state)
    logger.info("現在の状態は %s です", current_state)

    #変更がなければそのままにする
    if payload.new_state == current_state:
        logger.info("状態はすでに %s のため変更不要", payload.new_state)
        return QuoteStateUpdateModel(
            quote_id=str(quote_id), 
            from_state=current_state.value, 
            to_state=payload.new_state.value
        )

    #遷移しても良いかどうか確認
    allowed = ALLOWED_TRANSITIONS.get(current_state, [])
    if payload.new_state not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不正な状態遷移: {current_state} → {payload.new_state}"
        )

    #DBのquoteの状態を変更
    try:
        await mark_quote_state(session=session, quote_id=quote_id, user_id=user_id, new_state=payload.new_state.value)
        #イベントを発火
        event = QuoteStatusChangedEvent(
            quote_id=str(quote_id),
            from_state=current_state.value, 
            to_state=payload.new_state.value,
            changed_at=datetime.utcnow().isoformat()
        )

        await publish_event("quotes.QuoteUpdated", event.dict())

        return QuoteStateUpdateModel(
            quote_id=str(quote_id), 
            from_state=current_state.value, 
            to_state=payload.new_state.value
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# ------------------------------------------------------------------------------
# PATCH /my/quotes/{quote_id} - 見積もり内容の更新
# ------------------------------------------------------------------------------
@router.patch("/my/quotes/{quote_id}", response_model=PensionQuoteResponseModel)
async def patch_my_quote(
    quote_id: str = Path(..., description="対象の見積もりID"),
    updates: PartialQuoteUpdateModel = ...,
    token_payload: dict = Depends(require_quote_write_permission),
    session: AsyncSession = Depends(get_async_session),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):
    """
    指定された見積もりIDに対して、部分的な情報更新を行う。

    - 見積もりは「confirmed（確定）」状態である必要がある。
    - 更新対象フィールドが1つも指定されていない場合はエラー。
    - PostgreSQLのquote_detailsを更新。
    - シナリオはMongoDBに再保存。
    - 見積もり変更イベント（QuoteChanged）を発火。
    """
    user_id = token_payload.get("sub")
    logger.info(f"[PATCH] PATCH /my/quotes/{quote_id} by user_id={user_id}")

    # 1. 現在の見積もり情報を取得（JOIN済のレスポンスモデル）
    current_quote = await get_quote_by_id(session, UUID(quote_id), UUID(user_id))
    logger.debug(f"[DEBUG] current_quote dict: {current_quote.dict()}")

    # ステータスが 'confirmed' 以外は更新不可
    if current_quote.quote_state != "confirmed":
        raise HTTPException(status_code=400, detail="confirmed状態のみ更新可能です")

    # 2. 更新内容の検証
    update_dict = updates.dict(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="更新項目が指定されていません")
    
    update_fields = updates.dict(exclude_unset=True)
    logger.debug(f"[DEBUG] update_fields to update: {update_fields}")

    # 3. 既存情報と更新内容をマージし、再見積もり用のリクエストモデルを構築
    merged_data = current_quote.dict()
    merged_data.update(update_dict)

    new_request_model = PensionQuoteRequestModel(
        birth_date=updates.birth_date or current_quote.birth_date,
        gender=updates.gender or current_quote.gender,
        monthly_premium=updates.monthly_premium or current_quote.monthly_premium,
        payment_period_years=updates.payment_period_years or current_quote.payment_period_years,
        pension_payment_years=updates.pension_payment_years or current_quote.pension_payment_years,
        tax_deduction_enabled=(
            updates.tax_deduction_enabled
            if updates.tax_deduction_enabled is not None
            else current_quote.tax_deduction_enabled
        )
    )
    # 4. calculate_quote関数を使って再見積もり（MongoDBから金利取得等も含む）
    calculated_result = await calculate_quote(new_request_model, mongo_client, quote_id=UUID(quote_id))

    response_model = PensionQuoteResponseModel(
        quote_id=UUID(quote_id),
        user_id=UUID(user_id),
        quote_state=current_quote.quote_state,
        created_at=current_quote.created_at,
        updated_at=datetime.utcnow(),
        created_by=current_quote.created_by,
        updated_by=str(user_id),  # 変更者を記録
        birth_date=new_request_model.birth_date,
        gender=new_request_model.gender,
        monthly_premium=new_request_model.monthly_premium,
        payment_period_years=new_request_model.payment_period_years,
        pension_payment_years=new_request_model.pension_payment_years,
        tax_deduction_enabled=new_request_model.tax_deduction_enabled,
        contract_date=calculated_result.contract_date,
        contract_interest_rate=calculated_result.contract_interest_rate,
        total_paid_amount=calculated_result.total_paid_amount,
        pension_start_age=calculated_result.pension_start_age,
        annual_tax_deduction=calculated_result.annual_tax_deduction,
        scenarios=calculated_result.scenarios
    )

    # 5. quote_detailsテーブルを更新（契約条件・計算結果の上書き）
    await update_quote(
        session=session,
        quote_id=UUID(quote_id),
        user_id=UUID(user_id),
        updates=response_model
    )

    # 6. シナリオ情報をMongoDBに再保存（新しい内容で上書き）
    await save_scenarios_to_mongo(
        mongo_client=mongo_client,
        quote_id=quote_id,
        scenarios=calculated_result.scenarios,
    )
    
    # 7. QuoteChanged イベントをNATSで発火（変更履歴用途）
    await publish_event(
        subject="quotes.changed",
        payload={
            "event": "QuoteChanged",
            "quote_id": quote_id,
            "changed_at": datetime.utcnow().isoformat()
        }
    )

    # 8. DBから最新の見積もりを再取得（scenariosは手動で渡す）
    updated_quote = await get_quote_by_id(
        session=session,
        quote_id=UUID(quote_id),
        user_id=UUID(user_id)
    )

    # 9. scenarios を注入
    updated_quote.scenarios = calculated_result.scenarios

    # 10. 更新後の見積もり情報をレスポンスとして返却
    return updated_quote

# ------------------------------------------------------------------------------
# DELETE /my/quotes/{quote_id} - 見積もりを削除（状態をcancelledに変更）
# ------------------------------------------------------------------------------

#状態遷移の定義
ALLOWED_TRANSITIONS_CANCEL = {
    QuoteState.confirmed: [QuoteState.cancelled],
    QuoteState.applied: [QuoteState.cancelled],
}

@router.delete("/my/quotes/{quote_id}", response_model=QuoteStateUpdateModel)
async def update_quote_state(
    session: AsyncSession = Depends(get_async_session),
    quote_id: UUID = Path(..., description="削除対象の見積もりID"),
    token_payload: dict = Depends(require_quote_write_permission),
):
    user_id = token_payload.get("sub")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"[API] DELETE /my/quotes/{quote_id} 状態変更 (new_state=cancelled)")

    #変更前の状態を取得
    quote = await get_quote_by_id(session, quote_id, user_id)
    if not quote:
        raise HTTPException(status_code=404, detail="見積もりが見つかりません")
    current_state = QuoteState(quote.quote_state)
    logger.info("現在の状態は %s です", current_state)

    #変更がなければそのままにする
    if "cancelled" == current_state:
        logger.info("状態はすでにcancelledのため変更不要")
        return QuoteStateUpdateModel(
            quote_id=str(quote_id), 
            from_state=current_state.value, 
            to_state="cancelled"
        )

    #遷移しても良いかどうか確認
    allowed = ALLOWED_TRANSITIONS_CANCEL.get(current_state, [])
    if "cancelled" not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不正な状態遷移: {current_state} → cancelled"
        )

    #DBのquoteの状態を変更
    try:
        await mark_quote_state(session=session, quote_id=quote_id, user_id=user_id, new_state="cancelled")
        #イベントを発火
        event = QuoteStatusChangedEvent(
            quote_id=str(quote_id),
            from_state=current_state.value, 
            to_state="cancelled",
            changed_at=datetime.utcnow().isoformat()
        )

        await publish_event("quotes.QuoteUpdated", event.dict())

        return QuoteStateUpdateModel(
            quote_id=str(quote_id), 
            from_state=current_state.value, 
            to_state="cancelled"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# ------------------------------------------------------------------------------
# GET /my/quotes - 自ユーザーの見積もり一覧
# ------------------------------------------------------------------------------
@router.get("/my/quotes", response_model=List[PensionQuoteResponseModel])
async def get_my_quotes(
    token_payload: dict = Depends(require_quote_write_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    session: AsyncSession = Depends(get_async_session),
):
    user_id = token_payload.get("sub")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"[API] GET /my/quotes (user_id={user_id})")

    # PostgreSQLから見積もり一覧（scenariosなし）を取得
    quotes = await get_quotes_by_user_id(session, user_id)

    # 各見積もりに対してMongoDBからscenariosを補完
    for quote in quotes:
        scenarios = await get_scenarios_by_quote_id(mongo_client, str(quote.quote_id))
        quote.scenarios = scenarios  # 直接セット

    return quotes

# ------------------------------------------------------------------------------
# GET /my/quotes/{quote_id} - 自ユーザーの個別見積もり取得
# ------------------------------------------------------------------------------
@router.get("/my/quotes/{quote_id}", response_model=PensionQuoteResponseModel)
async def get_my_quote_by_id(
    quote_id: str = Path(..., description="取得対象の見積もりID"),
    token_payload: dict = Depends(require_quote_write_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    session: AsyncSession = Depends(get_async_session),
):
    user_id = token_payload.get("sub")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    quote = await get_quote_by_id(session, quote_id, user_id)

    # MongoDBからシナリオを取得
    scenarios = await get_scenarios_by_quote_id(mongo_client, quote_id)
    quote.scenarios = scenarios

    return quote