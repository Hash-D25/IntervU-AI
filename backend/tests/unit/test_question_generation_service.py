"""Question generation service unit tests."""

import json

from app.ai.providers.base import ChatMessage
from app.features.interview.planning.schemas import InterviewPlan, InterviewType
from app.features.interview.question_generation.schemas import (
    Difficulty,
    GeneratedQuestion,
    QuestionCategory,
    QuestionGenerationContext,
)
from app.features.interview.question_generation.service import QuestionGenerationService
from app.features.interview.question_generation.strategies.behavioral import (
    BehavioralQuestionStrategy,
)
from app.features.interview.question_generation.strategies.cs_fundamentals import (
    CsFundamentalsQuestionStrategy,
)
from app.features.interview.question_generation.strategies.dsa import DsaQuestionStrategy
from app.features.interview.question_generation.strategies.project import ProjectQuestionStrategy
from app.features.job_description.processing.schemas import ParsedJobDescription
from app.features.job_description.processing.seniority import SeniorityLevel
from app.features.resume.parsing.schemas import (
    EducationEntry,
    ExperienceEntry,
    ParsedResume,
    ProjectEntry,
)


class _FakeLLM:
    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, messages: list[ChatMessage]) -> str:
        self.calls += 1
        prompt = messages[0].content
        if "Category: DSA" in prompt:
            category = QuestionCategory.DSA
        elif "Category: PROJECT" in prompt:
            category = QuestionCategory.PROJECT
        elif "Category: BEHAVIORAL" in prompt:
            category = QuestionCategory.BEHAVIORAL
        else:
            category = QuestionCategory.CS_FUNDAMENTALS
        return json.dumps(
            {
                "text": f"Sample {category.value} question?",
                "expected_topics": ["topic-a", "topic-b"],
                "difficulty": "medium",
                "evaluation_rubric": ["clarity", "depth"],
            }
        )


def _sample_context() -> QuestionGenerationContext:
    return QuestionGenerationContext(
        company_name="EPAM",
        target_role="AI-Native Software Engineering Intern",
        interview_type=InterviewType.TECHNICAL,
        interview_plan=InterviewPlan(
            focus_areas=["Python", "FastAPI"],
            question_mix=["resume_deep_dive", "technical_core", "job_alignment"],
            estimated_rounds=2,
            follow_up_strategy="Ask follow-ups on weak areas.",
            evaluation_axes=["clarity", "depth"],
        ),
        resume=ParsedResume(
            skills=["Python", "FastAPI"],
            projects=[ProjectEntry(name="InterviewerAI", technologies=["FastAPI"])],
            experience=[ExperienceEntry(title="Engineer", company="Acme")],
            technologies=["PostgreSQL"],
            education=[EducationEntry(institution="Example University")],
            achievements=["Hackathon winner"],
        ),
        job_description=ParsedJobDescription(
            skills=["Communication"],
            technologies=["Python"],
            responsibilities=["Build APIs"],
            seniority_level=SeniorityLevel.INTERN,
        ),
        job_description_text="Intern role focused on AI-native engineering.",
    )


def _build_service(llm: _FakeLLM) -> QuestionGenerationService:
    kwargs = {"model": "llama-3.1-8b-instant", "disable_thinking": False}
    return QuestionGenerationService(
        {
            QuestionCategory.DSA: DsaQuestionStrategy(llm, **kwargs),  # type: ignore[arg-type]
            QuestionCategory.PROJECT: ProjectQuestionStrategy(llm, **kwargs),  # type: ignore[arg-type]
            QuestionCategory.BEHAVIORAL: BehavioralQuestionStrategy(llm, **kwargs),  # type: ignore[arg-type]
            QuestionCategory.CS_FUNDAMENTALS: CsFundamentalsQuestionStrategy(llm, **kwargs),  # type: ignore[arg-type]
        }
    )


async def test_question_generation_service_generates_per_plan_mix() -> None:
    llm = _FakeLLM()
    service = _build_service(llm)
    result = await service.generate(_sample_context())

    assert result.generator_name == "llm"
    assert len(result.questions) == 3
    assert result.questions[0].category == QuestionCategory.PROJECT
    assert result.questions[1].category == QuestionCategory.DSA
    assert result.questions[2].category == QuestionCategory.CS_FUNDAMENTALS
    assert llm.calls == 3


async def test_question_generation_service_returns_structured_questions() -> None:
    llm = _FakeLLM()
    service = _build_service(llm)
    result = await service.generate(_sample_context())
    question: GeneratedQuestion = result.questions[0]

    assert question.text.endswith("?")
    assert question.expected_topics
    assert question.evaluation_rubric
    assert question.difficulty == Difficulty.MEDIUM
