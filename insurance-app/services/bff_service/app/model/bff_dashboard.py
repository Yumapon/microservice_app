# -*- coding: utf-8 -*-
"""
/bff/my/dashboard 用レスポンスモデル定義
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# --- 見積もり情報モデル ---
class QuoteScenarioModel(BaseModel):
    scenario_type: str
    interest_rate: float
    estimated_pension: int
    annual_pension: int
    lump_sum_amount: int
    created_at: datetime

class QuoteModel(BaseModel):
    quote_id: UUID
    quote_state: str
    plan_code: str
    monthly_premium: int
    payment_period_years: int
    contract_date: datetime
    created_at: datetime
    scenarios: List[QuoteScenarioModel]


# --- 申込情報モデル ---
class ApplicationScenarioModel(BaseModel):
    scenario_type: str
    interest_rate: float
    estimated_pension: int
    annual_pension: int
    lump_sum_amount: int
    created_at: datetime

class ApplicationModel(BaseModel):
    application_id: UUID
    quote_id: UUID
    application_status: str
    monthly_premium: int
    contract_date: datetime
    plan_code: str
    applied_at: datetime
    scenarios: List[ApplicationScenarioModel]


# --- 契約情報モデル（想定） ---
class ContractModel(BaseModel):
    contract_id: UUID
    quote_id: UUID
    application_id: UUID
    plan_code: str
    monthly_premium: int
    contract_date: datetime
    contract_status: str


# --- ダッシュボード全体レスポンス ---
class DashboardResponseModel(BaseModel):
    quotes: List[QuoteModel]
    applications: List[ApplicationModel]
    contracts: List[ContractModel]
    unread_notifications: int = Field(..., description="未読通知件数")