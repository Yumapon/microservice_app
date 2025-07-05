# -*- coding: utf-8 -*-
"""
PostgreSQLとの非同期接続およびセッション管理

- config.yaml からDB接続設定（dsn, echo）を読み込み
- SQLAlchemyの AsyncSession を生成
- FastAPIのDepends連携で使用可能なセッションを提供
"""

# ------------------------------------------------------------------------------
# インポート
# ------------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import AsyncAttrs,AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config.config import Config

# ------------------------------------------------------------------------------
# 設定読み込み
# ------------------------------------------------------------------------------
config = Config()  # YAMLを読み込んで設定オブジェクトを生成
postgres_cfg = config.postgres
POSTGRES_DSN = postgres_cfg["dsn"]
ECHO_ENABLED = postgres_cfg.get("echo", False)  # echoが未設定の場合はFalse

# ------------------------------------------------------------------------------
# 非同期エンジンの作成（SQLAlchemy v2対応）
# ------------------------------------------------------------------------------
engine = create_async_engine(
    POSTGRES_DSN,
    echo=ECHO_ENABLED,  # config.yamlの設定に応じてSQLログ出力
    future=True,
)

# ------------------------------------------------------------------------------
# 非同期セッションファクトリ
# ------------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# ------------------------------------------------------------------------------
# FastAPIのDepends()対応：非同期セッションを提供する関数
# ------------------------------------------------------------------------------
async def get_async_session() -> AsyncSession:
    """
    非同期DBセッションを生成し、呼び出し元に提供する

    Usage:
        session: AsyncSession = Depends(get_async_session)
    """
    async with AsyncSessionLocal() as session:
        yield session
