"""Application entrypoint.

``create_app`` is a factory so tests can build isolated instances and override
dependencies. The engine and session factory live on ``app.state`` and are
managed by the lifespan context.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

# Register every ORM model before any route/service imports pull in a subset.
# Without this, string-based relationships (User -> "Interview") fail at runtime.
from app.db import registry as _registry  # noqa: F401
from app.db.engine import create_engine
from app.db.session import create_session_factory


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()
    engine = create_engine(settings.database_url)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    try:
        yield
    finally:
        await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title="InterviewerAI", version="0.1.0", lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
