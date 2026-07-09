"""Parsed resume profile ORM model - stored separately from raw file metadata."""

import enum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

JsonPayload = JSON().with_variant(JSONB, "postgresql")


class ParseStatus(enum.StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


def _enum_values(enum_cls: type[enum.StrEnum]) -> list[str]:
    return [member.value for member in enum_cls.__members__.values()]


class ResumeParsedProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "resume_parsed_profiles"

    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), unique=True, index=True
    )
    skills: Mapped[list[str]] = mapped_column(JsonPayload, default=list)
    projects: Mapped[list[dict[str, object]]] = mapped_column(JsonPayload, default=list)
    experience: Mapped[list[dict[str, object]]] = mapped_column(JsonPayload, default=list)
    technologies: Mapped[list[str]] = mapped_column(JsonPayload, default=list)
    education: Mapped[list[dict[str, object]]] = mapped_column(JsonPayload, default=list)
    achievements: Mapped[list[str]] = mapped_column(JsonPayload, default=list)
    parser_name: Mapped[str] = mapped_column(Text)
    parse_status: Mapped[ParseStatus] = mapped_column(
        Enum(ParseStatus, name="parse_status", values_callable=_enum_values),
        default=ParseStatus.PENDING,
    )
    parse_error: Mapped[str | None] = mapped_column(Text)
