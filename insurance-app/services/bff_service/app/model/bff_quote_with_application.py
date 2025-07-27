from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


class ContractConditionsModel(BaseModel):
    birth_date: date
    gender: str
    monthly_premium: int
    payment_period_years: int
    tax_deduction_enabled: bool
    pension_payment_years: int
    plan_code: str


class CalculationResultModel(BaseModel):
    contract_date: date
    contract_interest_rate: float
    total_paid_amount: int
    pension_start_age: int
    annual_tax_deduction: int


class ApplicationSummaryModel(BaseModel):
    application_id: UUID
    application_status: str
    application_number: Optional[str]
    applied_at: datetime
    payment_method: str
    user_consent: bool
    identity_verified: bool


class QuoteWithApplicationModel(BaseModel):
    quote_id: UUID
    quote_state: str
    created_at: datetime

    contract_conditions: ContractConditionsModel
    calculation_result: CalculationResultModel
    application: Optional[ApplicationSummaryModel]