"""Structured models for generated interview questions."""

from enum import StrEnum

from pydantic import BaseModel, Field

from app.features.interview.execution.schemas import InterviewPhase
from app.features.interview.planning.schemas import InterviewPlan, InterviewType
from app.features.job_description.processing.schemas import ParsedJobDescription
from app.features.resume.parsing.schemas import ParsedResume


class QuestionCategory(StrEnum):
    DSA = "dsa"
    PROJECT = "project"
    BEHAVIORAL = "behavioral"
    CS_FUNDAMENTALS = "cs_fundamentals"


class Difficulty(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class GeneratedQuestion(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    category: QuestionCategory
    expected_topics: list[str] = Field(default_factory=list)
    difficulty: Difficulty
    evaluation_rubric: list[str] = Field(default_factory=list)


class QuestionGenerationContext(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    target_role: str = Field(min_length=1, max_length=255)
    interview_type: InterviewType
    interview_plan: InterviewPlan
    resume: ParsedResume
    job_description: ParsedJobDescription | None = None
    job_description_text: str | None = None
    execution_phase: InterviewPhase | None = None
    phase_instruction: str | None = None
    focus_project_names: list[str] = Field(default_factory=list)
    comparison_project_names: list[str] = Field(default_factory=list)
    projects_already_covered: list[str] = Field(default_factory=list)
    previous_question_topics: list[str] = Field(default_factory=list)


class QuestionGenerationResult(BaseModel):
    questions: list[GeneratedQuestion] = Field(default_factory=list)
    generator_name: str
