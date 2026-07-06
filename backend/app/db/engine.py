"""Async SQLAlchemy engine factory.

The engine is created once per process during application startup (see
``app.main``) and disposed on shutdown.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def create_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True, future=True)
