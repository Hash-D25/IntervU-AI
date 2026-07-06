"""FeedbackReport ORM model (one report per interview)."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.features.interview.models import Interview

# JSONB on PostgreSQL, portable JSON elsewhere (keeps SQLite tests working).
StringList = JSON().with_variant(JSONB, "postgresql")


class FeedbackReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "feedback_reports"

    interview_id: Mapped[UUID] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), unique=True, index=True
    )
    summary: Mapped[str] = mapped_column(Text)
    strengths: Mapped[list[str]] = mapped_column(StringList, default=list)
    weaknesses: Mapped[list[str]] = mapped_column(StringList, default=list)
    suggestions: Mapped[list[str]] = mapped_column(StringList, default=list)
    roadmap: Mapped[list[str]] = mapped_column(StringList, default=list)
    overall_score: Mapped[float | None] = mapped_column(Float)

    interview: Mapped["Interview"] = relationship(back_populates="feedback_report")
