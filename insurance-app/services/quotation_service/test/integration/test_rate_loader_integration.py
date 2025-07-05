# test/integration/test_rate_loader_integration.py

import pytest
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.rate_loader import load_interest_rates

@pytest.mark.asyncio
async def test_load_interest_rates_with_real_mongo():
    # 実MongoDBクライアント（localhost接続）
    mongo_client = AsyncIOMotorClient("mongodb://localhost:27017")

    # テスト対象の契約日とプランコード
    plan_code = "PENSION_001"
    contract_date = datetime(2025, 8, 1, tzinfo=timezone.utc)

    # 呼び出し
    result = await load_interest_rates(
        db=mongo_client,
        plan_code=plan_code,
        contract_date=contract_date
    )

    assert result["contract_rate"] == 1.2
    assert result["min_rate"] == 0.5
    assert result["high_rate"] == 1.5
    assert result["annuity_conversion_rate"] == 0.8
    assert result["surrender_rates"]["15"] == 0.85