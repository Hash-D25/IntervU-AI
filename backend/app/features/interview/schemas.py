"""Interview creation request/response DTOs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.features.evaluation.schemas import AnswerEvaluationResult
from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.models import InterviewStatus
from app.features.interview.planning.schemas import (
    InterviewMetadata,
    InterviewPlan,
    InterviewType,
    SessionStateSnapshot,
)


class CreateInterviewRequest(BaseModel):
    resume_id: UUID
    company_name: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    interview_type: InterviewType
    job_description: str | None = Field(default=None, max_length=50_000)


class SubmitAnswerRequest(BaseModel):
    transcript: str = Field(min_length=1, max_length=20_000)


class AnswerEvaluationResponse(AnswerEvaluationResult):
    """Structured per-answer evaluation scores."""


class ExecutionSnapshotResponse(BaseModel):
    status: EngineStatus
    phase: InterviewPhase | None
    current_question: SessionQuestion | None
    previous_questions: list[SessionQuestion] = Field(default_factory=list)
    allowed_transitions: list[InterviewPhase] = Field(default_factory=list)
    session_context: SessionContext


class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    resume_id: UUID | None
    company_name: str | None
    target_role: str
    interview_type: InterviewType | None
    status: InterviewStatus
    session_state: SessionStateSnapshot
    interview_metadata: InterviewMetadata
    interview_plan: InterviewPlan
    job_description: str | None = None
    created_at: datetime
    updated_at: datetime
