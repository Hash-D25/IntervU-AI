"""Persisted answer evaluation scores."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

JsonPayload = JSON().with_variant(JSONB, "postgresql")

if TYPE_CHECKING:
    from app.features.interview.models import Answer


class AnswerEvaluation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "answer_evaluations"

    answer_id: Mapped[UUID] = mapped_column(
        ForeignKey("answers.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    overall_score: Mapped[float] = mapped_column(Float)
    scores: Mapped[list[dict[str, object]]] = mapped_column(JsonPayload, default=list)
    strengths: Mapped[list[str]] = mapped_column(JsonPayload, default=list)
    improvements: Mapped[list[str]] = mapped_column(JsonPayload, default=list)
    evaluator_name: Mapped[str] = mapped_column(String(64))

    answer: Mapped["Answer"] = relationship(back_populates="evaluation")
