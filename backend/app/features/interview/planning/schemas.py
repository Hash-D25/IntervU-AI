"""Interview planning and state machine schemas."""

from enum import StrEnum

from pydantic import BaseModel, Field


class InterviewType(StrEnum):
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    MIXED = "mixed"


class SessionState(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    ASKING_INTRO = "asking_intro"
    ASKING_CORE = "asking_core"
    ASKING_FOLLOW_UP = "asking_follow_up"
    AWAITING_ANSWER = "awaiting_answer"
    EVALUATING_ANSWER = "evaluating_answer"
    FINISHED = "finished"


class ResumeSummary(BaseModel):
    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    project_names: list[str] = Field(default_factory=list)
    experience_titles: list[str] = Field(default_factory=list)


class InterviewMetadata(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    interview_type: InterviewType
    has_job_description: bool
    resume_summary: ResumeSummary
    context_sources: list[str] = Field(default_factory=list)


class InterviewPlan(BaseModel):
    focus_areas: list[str] = Field(default_factory=list)
    question_mix: list[str] = Field(default_factory=list)
    estimated_rounds: int = Field(ge=1, le=10)
    follow_up_strategy: str = Field(min_length=1, max_length=500)
    evaluation_axes: list[str] = Field(default_factory=list)


class SessionStateSnapshot(BaseModel):
    current: SessionState
    allowed_transitions: list[SessionState] = Field(default_factory=list)
    question_index: int = Field(default=0, ge=0)
    answered_questions: int = Field(default=0, ge=0)


class InterviewBlueprint(BaseModel):
    metadata: InterviewMetadata
    session_state: SessionStateSnapshot
    interview_plan: InterviewPlan
