"""Structured output models for parsed job descriptions."""

from pydantic import BaseModel, Field, field_validator

from app.features.job_description.processing.seniority import (
    SeniorityLevel,
    normalize_seniority_level,
)


class ParsedJobDescription(BaseModel):
    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    seniority_level: SeniorityLevel = SeniorityLevel.UNSPECIFIED

    @field_validator("seniority_level", mode="before")
    @classmethod
    def coerce_seniority(cls, value: object) -> SeniorityLevel:
        if isinstance(value, SeniorityLevel):
            return value
        return normalize_seniority_level(str(value))
