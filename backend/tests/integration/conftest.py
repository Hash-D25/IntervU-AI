"""Shared fixtures for integration tests."""

from collections.abc import AsyncGenerator, Callable
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.registry import Base
from app.db.session import get_session
from app.main import create_app


async def build_integration_client(
    *,
    dependency_overrides: dict[Callable[..., Any], Callable[..., Any]] | None = None,
    settings_overrides: dict[str, Any] | None = None,
) -> AsyncGenerator[tuple[AsyncClient, AsyncEngine], None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        async with factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_get_session

    if settings_overrides:
        base_settings = get_settings().model_copy(update=settings_overrides)
        app.dependency_overrides[get_settings] = lambda: base_settings

    if dependency_overrides:
        app.dependency_overrides.update(dependency_overrides)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client, engine

    await engine.dispose()


@pytest.fixture
async def integration_client() -> AsyncGenerator[AsyncClient]:
    """SQLite-backed API client with no extra dependency overrides."""
    async for client, _engine in build_integration_client():
        yield client
