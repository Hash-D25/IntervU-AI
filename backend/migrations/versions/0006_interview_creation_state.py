"""interview creation state machine fields

Revision ID: 0006_interview_creation_state
Revises: 0005_parsed_achievements
Create Date: 2026-07-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_interview_creation_state"
down_revision: str | None = "0005_parsed_achievements"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INTERVIEW_TYPE = sa.Enum("technical", "behavioral", "mixed", name="interview_type")
_INTERVIEW_SESSION_STATE = sa.Enum(
    "draft",
    "ready",
    "asking_intro",
    "asking_core",
    "asking_follow_up",
    "awaiting_answer",
    "evaluating_answer",
    "finished",
    name="interview_session_state",
)
_JSON = sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), "postgresql")


def upgrade() -> None:
    bind = op.get_bind()
    _INTERVIEW_TYPE.create(bind, checkfirst=True)
    _INTERVIEW_SESSION_STATE.create(bind, checkfirst=True)

    op.add_column("interviews", sa.Column("resume_id", sa.Uuid(), nullable=True))
    op.add_column("interviews", sa.Column("interview_type", _INTERVIEW_TYPE, nullable=True))
    op.add_column("interviews", sa.Column("session_state", _INTERVIEW_SESSION_STATE, nullable=True))
    op.add_column(
        "interviews",
        sa.Column("interview_metadata", _JSON, nullable=False, server_default=sa.text("'{}'")),
    )
    op.add_column(
        "interviews",
        sa.Column("interview_plan", _JSON, nullable=False, server_default=sa.text("'{}'")),
    )
    op.create_index("ix_interviews_resume_id", "interviews", ["resume_id"], unique=False)
    op.create_foreign_key(
        "fk_interviews_resume_id_resumes",
        "interviews",
        "resumes",
        ["resume_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.alter_column("interviews", "interview_metadata", server_default=None)
    op.alter_column("interviews", "interview_plan", server_default=None)


def downgrade() -> None:
    op.drop_constraint("fk_interviews_resume_id_resumes", "interviews", type_="foreignkey")
    op.drop_index("ix_interviews_resume_id", table_name="interviews")
    op.drop_column("interviews", "interview_plan")
    op.drop_column("interviews", "interview_metadata")
    op.drop_column("interviews", "session_state")
    op.drop_column("interviews", "interview_type")
    op.drop_column("interviews", "resume_id")

    bind = op.get_bind()
    _INTERVIEW_SESSION_STATE.drop(bind, checkfirst=False)
    _INTERVIEW_TYPE.drop(bind, checkfirst=False)
