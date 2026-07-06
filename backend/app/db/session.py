"""Async session factory and the request-scoped session dependency.

The session factory is built at startup and stored on ``app.state`` so tests can
swap the engine without touching module-level globals.
"""

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:
    """Yield a session bound to the current request; always closed afterwards."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        yield session
