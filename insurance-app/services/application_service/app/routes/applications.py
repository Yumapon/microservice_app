# -*- coding: utf-8 -*-
"""
保険契約申込APIエンドポイント

- 申込の作成
- 自ユーザーの申込一覧・詳細の取得
- 自ユーザーの申込キャンセル（ステータス更新）
"""

import logging
from datetime import datetime
from uuid import uuid4, UUID
from typing import List
from fastapi import APIRouter, Depends, Path, HTTPException, status


from app.dependencies.auth import (
    require_application_write_permission, 
    require_application_read_permission
)
from app.models.applications import (
    PensionApplicationRequestModel,
    PensionApplicationResponseModel,
    QuoteSummaryModel,
    ApplicationState,
    ApplicationStatusUpdateRequest,
    ApplicationStatusUpdateModel,
    PartialApplicationUpdateModel,
    ApplicationBeneficiaryRequestModel
)
from app.services.fetch_quote import (
    fetch_quote_by_id
)
from app.services.application_manager import (
    save_application,
    get_applications_by_user_id,
    get_application_by_application_id,
    get_scenarios_by_application_id,
    update_application_status,
    update_application,
    save_beneficiaries_to_mongo,
    save_scenarios_to_mongo,
    get_beneficiaries_by_application_id,
)

from app.models.events import (
    ApplicationCreatedEvent,
    ApplicationStatusChangedEvent,
    ApplicationChangedEvent,
)
from app.services.nats_publisher import publish_event

from app.db.database import get_async_session

from motor.motor_asyncio import AsyncIOMotorClient
from app.dependencies.get_mongo_client import get_mongo_client
from app.logic.applications_check import validate_quote_before_application
from sqlalchemy.ext.asyncio import AsyncSession

# ------------------------------------------------------------------------------
# 設定・ロガー初期化
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------------------------------
# POST /applications/pension - 新しい見積もりを作成
# ------------------------------------------------------------------------------
@router.post("/applications/pension", response_model=PensionApplicationResponseModel)
async def post_application(
    request_model: PensionApplicationRequestModel,
    token_payload: dict = Depends(require_application_write_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    session: AsyncSession = Depends(get_async_session),
):
    """
    新規の保険申込を作成する（MongoDBの利率と整合性チェックを含む）

    Returns:
        ApplicationResponseModel: 登録された申込情報
    """
    user_id = token_payload.get("sub")

    logger.info(f"[API] POST /applications/pension called (user_id={user_id})")

    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    access_token = token_payload.get("access_token")
    quote_id = request_model.quote_id

    #見積もりを取得
    quote_dict = await fetch_quote_by_id(
        quote_id=quote_id, 
        access_token=access_token
    )

    #見積もりに問題がないかをチェック
    await validate_quote_before_application(
        user_id=user_id, 
        quote=quote_dict, 
        mongo_client=mongo_client
    )

    #モデル変換
    quote = QuoteSummaryModel.model_validate(quote_dict)

    #申し込みIDを生成
    application_id = uuid4()  # 新規発行用のID
    logger.info(f"[申し込みID発行]quote_id: {application_id}")

    # 申込実行
    await save_application(
        application_id = application_id,
        session = session,
        user_id = user_id, 
        quote = quote, 
        request = request_model,
    )
    await save_beneficiaries_to_mongo(
        mongo_client = mongo_client,
        application_id = str(application_id),
        beneficiaries = request_model.beneficiaries
    )
    await save_scenarios_to_mongo(
        mongo_client = mongo_client,
        application_id = str(application_id),
        scenarios = quote.scenarios
    )

    #イベントを発火
    event = ApplicationCreatedEvent(
        quote_id=quote_id,
        user_id=user_id,
        application_id=application_id,
        created_at=datetime.utcnow()
    )
    await publish_event("applications.ApplicationCreated", event.dict())

    #DBから最新データを取得してレスポンス構築
    created_application = await get_application_by_application_id(
        session=session,
        application_id=application_id,
        user_id=user_id
    )
    created_application_scenarios = await get_scenarios_by_application_id(
        mongo_client = mongo_client,
        application_id = str(application_id)
    )
    created_application_beneficiaries = await get_beneficiaries_by_application_id(
        mongo_client = mongo_client,
        application_id = str(application_id)
    )

    #シナリオをマージする
    created_application.scenarios = created_application_scenarios
    created_application.beneficiaries = created_application_beneficiaries

    return created_application

# ------------------------------------------------------------------------------
# PUT /my/applications/{application_id}/changestate
# ------------------------------------------------------------------------------
#状態遷移の定義
ALLOWED_TRANSITIONS = {
    ApplicationState.pending: [
        ApplicationState.under_review, 
        ApplicationState.cancelled
    ],
    ApplicationState.under_review: [
        ApplicationState.pending, 
        ApplicationState.confirmed, 
        ApplicationState.rejected
    ],
}
@router.put("/my/applications/{application_id}/changestate", response_model=ApplicationStatusUpdateModel)
async def update_application_satus(
    payload: ApplicationStatusUpdateRequest,
    session: AsyncSession = Depends(get_async_session),
    application_id: str = Path(..., description="変更対象の申込ID"),
    token_payload: dict = Depends(require_application_write_permission),
):

    logger.info(f"[API] PUT /my/applications/{application_id}/changestate 状態変更 (new_state={payload.new_state})")
    user_id = token_payload.get("sub")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    #変更前の状態を取得
    application = await get_application_by_application_id(session, application_id, user_id)
    if not application:
        raise HTTPException(status_code=404, detail="申し込みが見つかりません")
    current_state = ApplicationState(application.application_status)
    logger.info("現在の状態は %s です", current_state)

    #変更がなければそのままにする
    if payload.new_state == current_state:
        logger.info("状態はすでに %s のため変更不要", payload.new_state)
        return ApplicationStatusUpdateModel(
            application_id=str(application_id), 
            from_status=current_state, 
            to_status=payload.new_state
        )

    #遷移しても良いかどうか確認
    allowed = ALLOWED_TRANSITIONS.get(current_state, [])
    logger.debug(f"[遷移検証] {current_state} → {payload.new_state}, allowed: {allowed}")
    if payload.new_state not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不正な状態遷移: {current_state} → {payload.new_state}"
        )

    #DBのquoteの状態を変更
    try:
        await update_application_status(
            session=session, 
            application_id=application_id, 
            user_id=user_id, 
            new_status=payload.new_state.value
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    #イベントを発火
    event = ApplicationStatusChangedEvent(
        application_id=application_id,
        from_state=current_state.value, 
        to_state=payload.new_state.value,
        changed_at=datetime.utcnow().isoformat()
    )
    await publish_event("applications.ApplicationStatusChanged", event.dict())

    return ApplicationStatusUpdateModel(
        application_id=application_id, 
        from_status=current_state, 
        to_status=payload.new_state
    )

# ------------------------------------------------------------------------------
# PATCH /my/applications/{application_id}
# ------------------------------------------------------------------------------
@router.patch("/my/applications/{application_id}", response_model=PensionApplicationResponseModel)
async def patch_my_quote(
    application_id: str = Path(..., description="対象の見積もりID"),
    updates: PartialApplicationUpdateModel = ...,
    token_payload: dict = Depends(require_application_write_permission),
    session: AsyncSession = Depends(get_async_session),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
):

    user_id = token_payload.get("sub")
    logger.info(f"[PATCH] PATCH /my/applications/{application_id} by user_id={user_id}")

    # 1. 現在の申し込み情報を取得（JOIN済のレスポンスモデル）
    current_application = await get_application_by_application_id(session, application_id, user_id)
    logger.debug(f"[DEBUG] current_application dict: {current_application.dict()}")
    current_beneficiaries = await get_beneficiaries_by_application_id(
        mongo_client=mongo_client,
        application_id=application_id
    )

    # ステータスが 'pending' 以外は更新不可
    if current_application.application_status != "pending":
        raise HTTPException(status_code=400, detail="pendingd状態のみ更新可能です")

    # 2. 更新内容の検証
    update_dict = updates.dict(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="更新項目が指定されていません")
    
    update_fields = updates.dict(exclude_unset=True)
    logger.info(f"[DEBUG] update_fields to update: {update_fields}")

    if "quote_id" in update_dict and update_dict["quote_id"] is not None:
        logger.warning("quote_id は更新できません")

    # 3. 既存情報と更新内容をマージし、再見積もり用のリクエストモデルを構築
    merged_data = current_application.dict()
    merged_data.update(update_dict)

    # Mongoから受け取った beneficiaries（Pydanticモデルリスト）
    mongo_beneficiaries_data = current_beneficiaries[0].beneficiaries

    # model_dump で辞書化し、リクエストモデルに変換
    converted_beneficiaries = [
        ApplicationBeneficiaryRequestModel(**b.model_dump())
        for b in mongo_beneficiaries_data
    ]

    new_request_model = PensionApplicationRequestModel(
        quote_id = current_application.quote_id,
        user_consent = updates.user_consent if updates.user_consent is not None else current_application.user_consent,
        payment_method = updates.payment_method if updates.payment_method is not None else current_application.payment_method,
        identity_verified = updates.identity_verified if updates.identity_verified is not None else current_application.identity_verified,
        beneficiaries = (
            updates.beneficiaries 
            if updates.beneficiaries is not None and updates.beneficiaries != [] 
            else converted_beneficiaries
        )
    )

    # applicationテーブル、application_detailsテーブルを更新
    await update_application(
        session=session,
        application_id=UUID(application_id),
        user_id=UUID(user_id),
        updates=new_request_model
    )
    await save_beneficiaries_to_mongo(
        mongo_client = mongo_client,
        application_id = application_id,
        beneficiaries = new_request_model.beneficiaries
    )

    #イベントを発火
    event = ApplicationChangedEvent(
        application_id=application_id,
        changed_at=datetime.utcnow()
    )
    await publish_event("applications.ApplicationChanged", event.dict())

    #DBから最新データを取得してレスポンス構築
    updated_application = await get_application_by_application_id(
        session=session,
        application_id=application_id,
        user_id=user_id
    )
    updated_application_scenarios = await get_scenarios_by_application_id(
        mongo_client = mongo_client,
        application_id = application_id
    )
    updated_application_beneficiaries = await get_beneficiaries_by_application_id(
        mongo_client = mongo_client,
        application_id = application_id
    )

    #シナリオをマージする
    updated_application.scenarios = updated_application_scenarios
    updated_application.beneficiaries = updated_application_beneficiaries

    return updated_application


# ------------------------------------------------------------------------------
# DELETE /my/applications/{application_id}
# ------------------------------------------------------------------------------
#状態遷移の定義
ALLOWED_TRANSITIONS_CANCEL = {
    ApplicationState.pending: [ApplicationState.cancelled],
}

@router.delete("/my/applications/{application_id}", response_model=ApplicationStatusUpdateModel)
async def update_application_state(
    session: AsyncSession = Depends(get_async_session),
    application_id: str = Path(..., description="キャンセル対象の申込ID"),
    token_payload: dict = Depends(require_application_write_permission),
):
    user_id = token_payload.get("sub")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"[API] DELETE /my/applications/{application_id} 状態変更 (new_state=cancelled)")

    #変更前の状態を取得
    application = await get_application_by_application_id(session, application_id, user_id)
    if not application:
        raise HTTPException(status_code=404, detail="申し込みが見つかりません")
    current_state = ApplicationState(application.application_status)
    logger.info("現在の状態は %s です", current_state)

    #変更がなければそのままにする
    if "cancelled" == current_state:
        logger.info("状態はすでにcancelledのため変更不要")
        return ApplicationStatusUpdateModel(
            application_id=str(application_id), 
            from_status=current_state.value, 
            to_status="cancelled"
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
        await update_application_status(
            session=session, 
            application_id=application_id, 
            user_id=user_id, 
            new_status="cancelled"
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    #イベントを発火
    event = ApplicationStatusChangedEvent(
        application_id=application_id,
        from_state=current_state.value, 
        to_state="cancelled",
        changed_at=datetime.utcnow().isoformat()
    )
    await publish_event("applications.ApplicationStatusChanged", event.dict())

    return ApplicationStatusUpdateModel(
        application_id=application_id, 
        from_status=current_state.value, 
        to_status="cancelled"
    )

# ------------------------------------------------------------------------------
# GET /my/applications
# ------------------------------------------------------------------------------
@router.get("/my/applications", response_model=List[PensionApplicationResponseModel])
async def get_my_applications(
    token_payload: dict = Depends(require_application_read_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    session: AsyncSession = Depends(get_async_session),
):
    user_id = token_payload.get("sub")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"[API] GET /my/applications (user_id={user_id})")

    applications = await get_applications_by_user_id(
        session=session,
        user_id=user_id,
    )
    for application in applications:
        # シナリオを取得する
        scenarios = await get_scenarios_by_application_id(
            mongo_client = mongo_client,
            application_id = str(application.application_id)
        )
        application.scenarios = scenarios

        # 保険金代理受取人を取得する
        beneficiaries = await get_beneficiaries_by_application_id(
            mongo_client = mongo_client,
            application_id = str(application.application_id)
        )
        application.beneficiaries = beneficiaries

    return applications

# ------------------------------------------------------------------------------
# GET /my/applications/{application_id}
# ------------------------------------------------------------------------------
@router.get("/my/applications/{application_id}", response_model=PensionApplicationResponseModel)
async def get_my_application_by_id(
    application_id: str = Path(..., description="申込ID"),
    token_payload: dict = Depends(require_application_read_permission),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client),
    session: AsyncSession = Depends(get_async_session),
):
    logger.info(f"[API] GET /my/applications/{application_id}")
    user_id = token_payload.get("sub")
    if not user_id:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")
    
    application = await get_application_by_application_id(
        session = session, 
        application_id = application_id, 
        user_id = user_id
    )

    # シナリオを取得する
    scenarios = await get_scenarios_by_application_id(
        mongo_client = mongo_client,
        application_id = str(application.application_id)
    )
    application.scenarios = scenarios

    # 保険金代理受取人を取得する
    beneficiaries = await get_beneficiaries_by_application_id(
        mongo_client = mongo_client,
        application_id = str(application.application_id)
    )
    application.beneficiaries = beneficiaries

    return application
