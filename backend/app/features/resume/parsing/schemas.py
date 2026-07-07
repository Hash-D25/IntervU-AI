"""Structured output models for parsed resumes."""

from pydantic import BaseModel, Field


class ProjectEntry(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    technologies: list[str] = Field(default_factory=list)


class ExperienceEntry(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    duration: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)


class EducationEntry(BaseModel):
    institution: str = Field(min_length=1, max_length=255)
    degree: str | None = Field(default=None, max_length=255)
    year: str | None = Field(default=None, max_length=50)


class ParsedResume(BaseModel):
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
