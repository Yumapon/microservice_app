# -*- coding: utf-8 -*-
"""
契約情報APIエンドポイント

- 自ユーザーの契約一覧取得
- 自ユーザーの契約詳細取得
- 契約の明示的確定
- 契約のキャンセル（解約）
"""

import logging
from fastapi import APIRouter, Depends, Path, HTTPException, status
from typing import List

from app.dependencies.auth import (
    require_contract_read_permission,
    require_contract_write_permission
)
from app.models.contracts import (
    ContractResponseModel,
    ContractCreateRequestModel,
    ContractUpdateModel
)
from app.services.contract_manager import (
    get_contracts_by_user_id,
    get_contract_by_id,
    create_contract_by_application_id,
    cancel_contract,
    update_contract
)

logger = logging.getLogger(__name__)
router = APIRouter()

# ------------------------------------------------------
# GET /my/contracts
# ------------------------------------------------------
@router.get("/my/contracts", response_model=List[ContractResponseModel])
async def get_my_contracts(
    token_payload: dict = Depends(require_contract_read_permission)
):
    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"【API】/api/v1/my/contracts 呼び出し (user_id={user_id_from_token})")
    return await get_contracts_by_user_id(user_id_from_token)

# ------------------------------------------------------
# GET /my/contracts/{contract_id}
# ------------------------------------------------------
@router.get("/my/contracts/{contract_id}", response_model=ContractResponseModel)
async def get_my_contract_by_id(
    contract_id: str = Path(..., description="取得対象の契約ID"),
    token_payload: dict = Depends(require_contract_read_permission)
):
    logger.info(f"【API】/api/v1/my/contracts/{contract_id} 呼び出し")

    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    contract = await get_contract_by_id(contract_id)

    user_id_from_contract = contract.user_id
    logger.info(f"検索した契約を作成したユーザ (user_id={user_id_from_contract})")
    logger.info(f"トークンから取得したユーザID (user_id={user_id_from_token})")
    if user_id_from_contract != user_id_from_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="他人の契約情報は参照できません")

    return contract

# ------------------------------------------------------
# PUT /my/contracts/{contract_id}
# ------------------------------------------------------
@router.put("/my/contracts/{contract_id}", response_model=ContractResponseModel)
async def update_my_contract(
    update_model: ContractUpdateModel,
    contract_id: str = Path(..., description="更新対象の契約ID"),
    token_payload: dict = Depends(require_contract_write_permission)
):
    logger.info(f"【API】/api/v1/my/contracts/{contract_id} 更新呼び出し")

    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    updated_contract = await update_contract(contract_id, user_id_from_token, update_model.dict(exclude_unset=True))
    return updated_contract

# ------------------------------------------------------
# POST /contracts/confirm
# ------------------------------------------------------
@router.post("/contracts/confirm", response_model=ContractResponseModel)
async def confirm_contract(
    request_model: ContractCreateRequestModel,
    token_payload: dict = Depends(require_contract_write_permission)
):
    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    logger.info(f"【API】/api/v1/contracts/confirm 契約確定呼び出し (application_id={request_model.application_id})")
    contract = await create_contract_by_application_id(request_model.application_id, user_id_from_token)
    return contract

# ------------------------------------------------------
# PUT /my/contracts/{contract_id}/cancel
# ------------------------------------------------------
@router.put("/my/contracts/{contract_id}/cancel", response_model=ContractResponseModel)
async def cancel_my_contract(
    contract_id: str = Path(..., description="キャンセル対象の契約ID"),
    token_payload: dict = Depends(require_contract_write_permission)
):
    logger.info(f"【API】/api/v1/my/contracts/{contract_id}/cancel 契約キャンセル呼び出し")

    user_id_from_token = token_payload.get("sub")
    if not user_id_from_token:
        logger.warning("アクセストークンにsubが含まれていません")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: no user ID")

    contract = await cancel_contract(contract_id, user_id_from_token)
    return contract
