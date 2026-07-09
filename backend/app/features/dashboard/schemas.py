"""Dashboard response models."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.features.interview.models import InterviewStatus
from app.features.interview.planning.schemas import InterviewType


class InterviewHistoryItem(BaseModel):
    id: UUID
    company_name: str | None
    target_role: str
    interview_type: InterviewType | None
    status: InterviewStatus
    created_at: datetime
    updated_at: datetime
    answered_count: int = Field(default=0, ge=0)
    overall_score: float | None = Field(default=None, ge=0, le=10)
    has_feedback: bool = False


class CategoryScore(BaseModel):
    category: str = Field(min_length=1, max_length=64)
    average_score: float = Field(ge=0, le=10)
    answer_count: int = Field(ge=1)


class ProgressPoint(BaseModel):
    interview_id: UUID
    label: str = Field(min_length=1, max_length=255)
    recorded_at: datetime
    overall_score: float = Field(ge=0, le=10)


class DashboardSummary(BaseModel):
    interview_history: list[InterviewHistoryItem] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    category_scores: list[CategoryScore] = Field(default_factory=list)
    dimension_averages: dict[str, float] = Field(default_factory=dict)
    progress_over_time: list[ProgressPoint] = Field(default_factory=list)
    total_interviews: int = Field(default=0, ge=0)
    completed_interviews: int = Field(default=0, ge=0)
