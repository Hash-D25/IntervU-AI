"""Add achievements column to resume_parsed_profiles.

Revision ID: 0005_parsed_achievements
Revises: 0004_resume_parsed_profiles
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_parsed_achievements"
down_revision: str | None = "0004_resume_parsed_profiles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "resume_parsed_profiles",
        sa.Column(
            "achievements",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.alter_column("resume_parsed_profiles", "achievements", server_default=None)


def downgrade() -> None:
    op.drop_column("resume_parsed_profiles", "achievements")
