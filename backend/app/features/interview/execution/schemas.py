"""Explicit session models for the interview execution engine."""

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from app.features.evaluation.schemas import AnswerEvaluationResult
from app.features.interview.planning.schemas import InterviewType


class InterviewPhase(StrEnum):
    INTRODUCTION = "introduction"
    RESUME = "resume"
    PROJECTS = "projects"
    CS_FUNDAMENTALS = "cs_fundamentals"
    BEHAVIORAL = "behavioral"
    FINAL = "final"


class EngineStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SessionQuestion(BaseModel):
    id: UUID | None = None
    position: int = Field(ge=0)
    phase: InterviewPhase
    text: str = Field(min_length=1, max_length=2000)
    category: str = Field(min_length=1, max_length=64)
    difficulty: str = Field(min_length=1, max_length=16)
    expected_topics: list[str] = Field(default_factory=list)
    evaluation_rubric: list[str] = Field(default_factory=list)
    answered: bool = False
    answer_transcript: str | None = None
    evaluation: AnswerEvaluationResult | None = None


class SessionContext(BaseModel):
    """All engine state lives here — nothing is implied elsewhere."""

    status: EngineStatus = EngineStatus.NOT_STARTED
    phase: InterviewPhase | None = None
    interview_type: InterviewType
    company_name: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    phase_sequence: list[InterviewPhase] = Field(default_factory=list)
    questions_per_phase: dict[InterviewPhase, int] = Field(default_factory=dict)
    questions: list[SessionQuestion] = Field(default_factory=list)
    awaiting_answer: bool = False
    started_at: datetime | None = None
    completed_at: datetime | None = None


class EngineSnapshot(BaseModel):
    status: EngineStatus
    phase: InterviewPhase | None
    current_question: SessionQuestion | None
    previous_questions: list[SessionQuestion] = Field(default_factory=list)
    allowed_transitions: list[InterviewPhase] = Field(default_factory=list)
    session_context: SessionContext
