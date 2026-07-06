"""initial schema: users, interviews, questions, answers, feedback_reports

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-06

Hand-written (Docker/Postgres was unavailable for --autogenerate). Targets
PostgreSQL: native ENUM types and JSONB columns. Constraint/index names follow
the project naming convention configured on ``Base.metadata``.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TIMESTAMP = sa.DateTime(timezone=True)
_NOW = sa.text("now()")

_INTERVIEW_STATUS = sa.Enum(
    "created", "in_progress", "completed", "abandoned", name="interview_status"
)
_QUESTION_KIND = sa.Enum("technical", "behavioral", "follow_up", name="question_kind")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.Column("updated_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "interviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("job_description", sa.Text(), nullable=True),
        sa.Column("status", _INTERVIEW_STATUS, nullable=False),
        sa.Column("created_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.Column("updated_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_interviews_user_id_users", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_interviews"),
    )
    op.create_index("ix_interviews_user_id", "interviews", ["user_id"], unique=False)

    op.create_table(
        "questions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("interview_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("kind", _QUESTION_KIND, nullable=False),
        sa.Column("created_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.Column("updated_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["interview_id"],
            ["interviews.id"],
            name="fk_questions_interview_id_interviews",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_questions"),
    )
    op.create_index("ix_questions_interview_id", "questions", ["interview_id"], unique=False)

    op.create_table(
        "answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("created_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.Column("updated_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
            name="fk_answers_question_id_questions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_answers"),
    )
    op.create_index("ix_answers_question_id", "answers", ["question_id"], unique=True)

    op.create_table(
        "feedback_reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("interview_id", sa.Uuid(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("strengths", postgresql.JSONB(), nullable=False),
        sa.Column("weaknesses", postgresql.JSONB(), nullable=False),
        sa.Column("suggestions", postgresql.JSONB(), nullable=False),
        sa.Column("roadmap", postgresql.JSONB(), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("created_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.Column("updated_at", _TIMESTAMP, server_default=_NOW, nullable=False),
        sa.ForeignKeyConstraint(
            ["interview_id"],
            ["interviews.id"],
            name="fk_feedback_reports_interview_id_interviews",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_feedback_reports"),
    )
    op.create_index(
        "ix_feedback_reports_interview_id", "feedback_reports", ["interview_id"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_feedback_reports_interview_id", table_name="feedback_reports")
    op.drop_table("feedback_reports")
    op.drop_index("ix_answers_question_id", table_name="answers")
    op.drop_table("answers")
    op.drop_index("ix_questions_interview_id", table_name="questions")
    op.drop_table("questions")
    op.drop_index("ix_interviews_user_id", table_name="interviews")
    op.drop_table("interviews")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    _QUESTION_KIND.drop(op.get_bind(), checkfirst=False)
    _INTERVIEW_STATUS.drop(op.get_bind(), checkfirst=False)
