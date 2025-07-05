# tests/services/test_rate_loader.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "./../../../")))

import pytest
import asyncio
from datetime import datetime, timezone
from app.services.rate_loader import load_interest_rates

@pytest.mark.asyncio
async def test_load_interest_rates_success(mocker):
    # --- モック用データ ---
    mock_record = {
        "contract_rate": 1.2,
        "min_rate": 0.5,
        "annuity_conversion_rate": 0.8,
        "surrender_rates": {"15": 0.85, "20": 0.92}
    }

    # --- Mongoクライアントをモック ---
    mock_db = mocker.Mock()
    mock_collection = mocker.AsyncMock()
    mock_collection.find_one.return_value = mock_record
    mock_db.get_database.return_value.get_collection.return_value = mock_collection

    # --- 実行対象 ---
    result = await load_interest_rates(
        db=mock_db,
        plan_code="PENSION_001",
        contract_date=datetime(2025, 8, 1, tzinfo=timezone.utc)
    )

    assert result["contract_rate"] == 1.2
    assert result["high_rate"] == 1.5
    assert result["surrender_rates"]["15"] == 0.85

@pytest.mark.asyncio
async def test_load_interest_rates_not_found(mocker):
    # --- find_one が None を返す ---
    mock_db = mocker.Mock()
    mock_collection = mocker.AsyncMock()
    mock_collection.find_one.return_value = None
    mock_db.get_database.return_value.get_collection.return_value = mock_collection

    with pytest.raises(ValueError) as exc_info:
        await load_interest_rates(
            db=mock_db,
            plan_code="PENSION_001",
            contract_date=datetime(2025, 8, 1, tzinfo=timezone.utc)
        )

    assert "利率情報が見つかりません" in str(exc_info.value)

@pytest.mark.asyncio
async def test_load_interest_rates_tz_naive_vs_aware(mocker):
    """tz-aware と naive datetime が一致するかどうかの検証"""
    mock_record = {
        "contract_rate": 1.2,
        "min_rate": 0.5,
        "annuity_conversion_rate": 0.8,
        "surrender_rates": {"15": 0.85, "20": 0.92}
    }

    # モック設定
    mock_db = mocker.Mock()
    mock_collection = mocker.AsyncMock()
    mock_collection.find_one.return_value = mock_record
    mock_db.get_database.return_value.get_collection.return_value = mock_collection

    # naive datetime を渡してみる
    naive_date = datetime(2025, 8, 1)  # tzなし

    result = await load_interest_rates(
        db=mock_db,
        plan_code="PENSION_001",
        contract_date=naive_date
    )

    assert result["contract_rate"] == 1.2