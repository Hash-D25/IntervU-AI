"""Interview memory models — rolling summary rebuilt from session answers."""

from uuid import UUID

from pydantic import BaseModel, Field


class MemoryAnswerSnippet(BaseModel):
    question_id: UUID | None = None
    position: int = Field(ge=0)
    phase: str = Field(min_length=1, max_length=64)
    category: str = Field(min_length=1, max_length=64)
    is_follow_up: bool = False
    question_text: str = Field(min_length=1, max_length=200)
    answer_excerpt: str = Field(min_length=1, max_length=500)
    mentioned_topics: list[str] = Field(default_factory=list)
    overall_score: float | None = Field(default=None, ge=0, le=10)
    strengths: list[str] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    key_claims: list[str] = Field(default_factory=list)


class InterviewMemory(BaseModel):
    """Compact recall state shared by question generation and follow-ups.

    v1 rebuilds this from ``SessionContext.questions`` after each answer.
    Stored on ``SessionContext.memory`` for prompt injection and future
    persistence strategies (DB / vector store).
    """

    answers: list[MemoryAnswerSnippet] = Field(default_factory=list)
    topics_covered: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weak_areas: list[str] = Field(default_factory=list)
    notable_mentions: list[str] = Field(default_factory=list)
    projects_discussed: list[str] = Field(default_factory=list)
    dimension_averages: dict[str, float] = Field(default_factory=dict)
    updated_from_question_count: int = Field(default=0, ge=0)
