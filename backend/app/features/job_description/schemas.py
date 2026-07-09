"""Job description API DTOs."""

from pydantic import BaseModel, Field

from app.features.job_description.processing.seniority import SeniorityLevel


class AnalyzeJobDescriptionRequest(BaseModel):
    text: str = Field(min_length=50, max_length=50_000)


class JobDescriptionAnalysisResponse(BaseModel):
    skills: list[str]
    technologies: list[str]
    responsibilities: list[str]
    seniority_level: SeniorityLevel
    analyzer_name: str
    extracted_text: str | None = None
