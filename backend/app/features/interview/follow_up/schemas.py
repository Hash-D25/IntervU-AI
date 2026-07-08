"""Follow-up generation schemas."""

from pydantic import BaseModel, Field

from app.features.evaluation.schemas import AnswerEvaluationResult
from app.features.interview.execution.schemas import InterviewPhase
from app.features.interview.memory.schemas import InterviewMemory


class ExtractedClaim(BaseModel):
    text: str = Field(min_length=1, max_length=500)
    claim_type: str = Field(default="technical", min_length=1, max_length=64)
    probe_angle: str = Field(min_length=1, max_length=500)


class FollowUpContext(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    phase: InterviewPhase
    category: str = Field(min_length=1, max_length=64)
    question_text: str = Field(min_length=1, max_length=2000)
    answer_transcript: str = Field(min_length=1, max_length=20_000)
    evaluation: AnswerEvaluationResult | None = None
    follow_up_strategy: str = Field(default="", max_length=500)
    focus_areas: list[str] = Field(default_factory=list)
    previous_follow_ups: list[str] = Field(default_factory=list)
    current_depth: int = Field(default=0, ge=0)
    max_depth: int = Field(default=1, ge=0)
    interview_follow_ups_used: int = Field(default=0, ge=0)
    max_interview_follow_ups: int = Field(default=3, ge=0)
    memory: InterviewMemory | None = None


class GeneratedFollowUp(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=64)
    difficulty: str = Field(min_length=1, max_length=16)
    expected_topics: list[str] = Field(default_factory=list)
    evaluation_rubric: list[str] = Field(default_factory=list)
    probed_claims: list[str] = Field(default_factory=list)
    generator_name: str = Field(min_length=1, max_length=64)


class FollowUpDecision(BaseModel):
    should_follow_up: bool
    reason: str = Field(min_length=1, max_length=500)
    claims: list[ExtractedClaim] = Field(default_factory=list)
    follow_up: GeneratedFollowUp | None = None
