"""Resume request/response DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.resume.parsed_models import ParseStatus
from app.features.resume.parsing.schemas import (
    EducationEntry,
    ExperienceEntry,
    ProjectEntry,
)


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    original_filename: str
    stored_path: str
    file_url: str | None = None
    file_size_bytes: int
    content_type: str
    created_at: datetime


class ParsedProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resume_id: UUID
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    parser_name: str
    parse_status: ParseStatus
    parse_error: str | None = None
    created_at: datetime
    updated_at: datetime
