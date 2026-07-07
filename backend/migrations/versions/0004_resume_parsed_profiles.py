"""resume_parsed_profiles table

Revision ID: 0004_resume_parsed_profiles
Revises: 0003_resumes
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_resume_parsed_profiles"
down_revision: str | None = "0003_resumes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TIMESTAMP = sa.DateTime(timezone=True)
_NOW = sa.text("now()")
_PARSE_STATUS = sa.Enum("pending", "completed", "failed", name="parse_status")


def upgrade() -> None:
    op.create_table(
        "resume_parsed_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("resume_id", sa.Uuid(), nullable=False),
        sa.Column("skills", postgresql.JSONB(), nullable=False),
        sa.Column("projects", postgresql.JSONB(), nullable=False),
        sa.Column("experience", postgresql.JSONB(), nullable=False),
        sa.Column("technologies", postgresql.JSONB(), nullable=False),
        sa.Column("education", postgresql.JSONB(), nullable=False),
        sa.Column("parser_name", sa.Text(), nullable=False),
        sa.Column("parse_status", _PARSE_STATUS, nullable=False),
        sa.Column("parse_error", sa.Text(), nullable=True),
        sa.Column("created_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.Column("updated_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
            name="fk_resume_parsed_profiles_resume_id_resumes",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_resume_parsed_profiles"),
    )
    op.create_index(
        "ix_resume_parsed_profiles_resume_id",
        "resume_parsed_profiles",
        ["resume_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_resume_parsed_profiles_resume_id", table_name="resume_parsed_profiles")
    op.drop_table("resume_parsed_profiles")
    _PARSE_STATUS.drop(op.get_bind(), checkfirst=False)
