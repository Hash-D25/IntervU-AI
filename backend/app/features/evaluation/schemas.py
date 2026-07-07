"""Answer evaluation request/response models."""

from enum import StrEnum

from pydantic import BaseModel, Field


class EvaluationDimension(StrEnum):
    TECHNICAL_ACCURACY = "technical_accuracy"
    COMPLETENESS = "completeness"
    COMMUNICATION = "communication"
    DEPTH = "depth"
    EXAMPLES = "examples"


REQUIRED_DIMENSIONS: tuple[EvaluationDimension, ...] = (
    EvaluationDimension.TECHNICAL_ACCURACY,
    EvaluationDimension.COMPLETENESS,
    EvaluationDimension.COMMUNICATION,
    EvaluationDimension.DEPTH,
    EvaluationDimension.EXAMPLES,
)


class DimensionScore(BaseModel):
    dimension: EvaluationDimension
    score: float = Field(ge=0, le=10)
    rationale: str = Field(min_length=1, max_length=500)


class AnswerEvaluationResult(BaseModel):
    scores: list[DimensionScore]
    overall_score: float = Field(ge=0, le=10)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    evaluator_name: str = Field(min_length=1, max_length=64)


class EvaluationContext(BaseModel):
    question_text: str = Field(min_length=1, max_length=2000)
    answer_transcript: str = Field(min_length=1, max_length=20_000)
    category: str = Field(min_length=1, max_length=64)
    phase: str = Field(min_length=1, max_length=64)
    difficulty: str = Field(min_length=1, max_length=16)
    expected_topics: list[str] = Field(default_factory=list)
    evaluation_rubric: list[str] = Field(default_factory=list)
    company_name: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
