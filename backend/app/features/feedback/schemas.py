"""Feedback generation request/response models."""

from pydantic import BaseModel, Field

from app.features.evaluation.schemas import DimensionScore


class EvaluatedAnswerSummary(BaseModel):
    position: int = Field(ge=0)
    phase: str = Field(min_length=1, max_length=64)
    category: str = Field(min_length=1, max_length=64)
    question_text: str = Field(min_length=1, max_length=2000)
    answer_transcript: str = Field(min_length=1, max_length=20_000)
    overall_score: float = Field(ge=0, le=10)
    dimension_scores: list[DimensionScore] = Field(default_factory=list)
    answer_strengths: list[str] = Field(default_factory=list)
    answer_improvements: list[str] = Field(default_factory=list)


class FeedbackContext(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    interview_type: str = Field(min_length=1, max_length=32)
    evaluated_answers: list[EvaluatedAnswerSummary] = Field(min_length=1)
    overall_average_score: float = Field(ge=0, le=10)
    dimension_averages: dict[str, float] = Field(default_factory=dict)
    recurring_strengths: list[str] = Field(default_factory=list)
    recurring_improvements: list[str] = Field(default_factory=list)


class FeedbackResult(BaseModel):
    summary: str = Field(min_length=1, max_length=2000)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    learning_roadmap: list[str] = Field(default_factory=list)
    overall_score: float = Field(ge=0, le=10)
    generator_name: str = Field(min_length=1, max_length=64)
