"""Interview aggregate: Interview and its Questions and Answers.

Kept in one module because these models are tightly coupled through
relationships and form a single aggregate rooted at ``Interview``.
"""

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin
from app.features.interview.planning.schemas import InterviewType, SessionState

JsonPayload = JSON().with_variant(JSONB, "postgresql")

if TYPE_CHECKING:
    from app.features.feedback.models import FeedbackReport
    from app.features.user.models import User


class InterviewStatus(enum.StrEnum):
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuestionKind(enum.StrEnum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    FOLLOW_UP = "follow_up"


def _enum_values(enum_cls: type[enum.StrEnum]) -> list[str]:
    return [member.value for member in enum_cls.__members__.values()]


class Interview(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "interviews"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    resume_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), index=True, nullable=True
    )
    role: Mapped[str] = mapped_column(String(255))
    company: Mapped[str | None] = mapped_column(String(255))
    job_description: Mapped[str | None] = mapped_column(Text)
    interview_type: Mapped[InterviewType | None] = mapped_column(
        Enum(InterviewType, name="interview_type", values_callable=_enum_values),
        nullable=True,
    )
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus, name="interview_status", values_callable=_enum_values),
        default=InterviewStatus.CREATED,
    )
    session_state: Mapped[SessionState | None] = mapped_column(
        Enum(SessionState, name="interview_session_state", values_callable=_enum_values),
        default=SessionState.READY,
        nullable=True,
    )
    interview_metadata: Mapped[dict[str, object]] = mapped_column(JsonPayload, default=dict)
    interview_plan: Mapped[dict[str, object]] = mapped_column(JsonPayload, default=dict)

    user: Mapped["User"] = relationship(back_populates="interviews")
    questions: Mapped[list["Question"]] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="Question.position",
    )
    feedback_report: Mapped["FeedbackReport | None"] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
    )


class Question(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "questions"

    interview_id: Mapped[UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    text: Mapped[str] = mapped_column(Text)
    kind: Mapped[QuestionKind] = mapped_column(
        Enum(QuestionKind, name="question_kind", values_callable=_enum_values),
        default=QuestionKind.TECHNICAL,
    )

    interview: Mapped["Interview"] = relationship(back_populates="questions")
    answer: Mapped["Answer | None"] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )


class Answer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "answers"

    question_id: Mapped[UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), unique=True, index=True
    )
    transcript: Mapped[str] = mapped_column(Text)

    question: Mapped["Question"] = relationship(back_populates="answer")
