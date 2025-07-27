# tests/conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.dependencies.get_mongo_client import get_mongo_client
from app.config.config import Config

@pytest.fixture(scope="session")
def config():
    return Config()

@pytest_asyncio.fixture
async def mongo_client(config):
    client = AsyncIOMotorClient(config.mongodb["dsn"])
    yield client
    client.close()

@pytest_asyncio.fixture
async def test_client(mongo_client):
    app.dependency_overrides[get_mongo_client] = lambda: mongo_client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides = {}