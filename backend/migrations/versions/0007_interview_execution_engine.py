"""interview execution engine context

Revision ID: 0007_interview_execution_engine
Revises: 0006_interview_creation_state
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_interview_execution_engine"
down_revision: str | None = "0006_interview_creation_state"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.add_column(
        "interviews",
        sa.Column("execution_context", _JSON, nullable=False, server_default=sa.text("'{}'")),
    )
    op.alter_column("interviews", "execution_context", server_default=None)


def downgrade() -> None:
    op.drop_column("interviews", "execution_context")
