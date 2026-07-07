"""answer evaluation scores

Revision ID: 0008_answer_evaluations
Revises: 0007_interview_execution_engine
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_answer_evaluations"
down_revision: str | None = "0007_interview_execution_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    op.create_table(
        "answer_evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("answer_id", sa.Uuid(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("scores", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("strengths", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("improvements", _JSON, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("evaluator_name", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["answer_id"],
            ["answers.id"],
            name="fk_answer_evaluations_answer_id_answers",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_answer_evaluations"),
    )
    op.create_index(
        "ix_answer_evaluations_answer_id",
        "answer_evaluations",
        ["answer_id"],
        unique=True,
    )
    op.alter_column("answer_evaluations", "scores", server_default=None)
    op.alter_column("answer_evaluations", "strengths", server_default=None)
    op.alter_column("answer_evaluations", "improvements", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_answer_evaluations_answer_id", table_name="answer_evaluations")
    op.drop_table("answer_evaluations")
