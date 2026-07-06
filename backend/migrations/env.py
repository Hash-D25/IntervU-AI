"""Alembic environment (synchronous).

Migrations run with a *synchronous* engine. This is simpler and fully
cross-platform — it avoids the async event-loop constraints some drivers hit on
Windows (psycopg's async mode cannot use the default ProactorEventLoop). The
application itself remains async; only migrations run sync.

The URL comes from application settings, and ``target_metadata`` is the shared
``Base.metadata``. Importing the registry registers every model so autogenerate
can detect them.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.config import get_settings
from app.db.registry import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    return get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(_database_url())
    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata, compare_type=True
            )
            with context.begin_transaction():
                context.run_migrations()
    finally:
        connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
