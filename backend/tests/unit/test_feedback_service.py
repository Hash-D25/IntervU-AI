"""Feedback service unit tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.registry import Base
from app.features.evaluation.schemas import (
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationDimension,
)
from app.features.feedback.repository import FeedbackReportRepository
from app.features.feedback.schemas import FeedbackContext, FeedbackResult
from app.features.feedback.service import FeedbackService
from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.models import Interview, InterviewStatus
from app.features.interview.planning.schemas import InterviewType
from app.features.interview.repository import InterviewRepository
from app.features.user.models import User


class FakeFeedbackGenerator:
    name = "fake"

    async def generate(self, context: FeedbackContext) -> FeedbackResult:
        return FeedbackResult(
            summary="Strong performance with room to deepen technical answers.",
            strengths=["Clear communication", "Good project storytelling"],
            weaknesses=["System design depth can improve"],
            recommendations=["Practice explaining tradeoffs out loud"],
            learning_roadmap=[
                "Week 1: review authentication patterns",
                "Week 2: mock system design sessions",
            ],
            overall_score=context.overall_average_score,
            generator_name=self.name,
        )


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session

    await engine.dispose()


def _evaluation() -> AnswerEvaluationResult:
    return AnswerEvaluationResult(
        scores=[
            DimensionScore(
                dimension=dim,
                score=8.0,
                rationale="Solid.",
            )
            for dim in EvaluationDimension
        ],
        overall_score=8.0,
        strengths=["Clear"],
        improvements=["More depth"],
        evaluator_name="llm",
    )


async def _seed_completed_interview(session: AsyncSession) -> tuple[Interview, User]:
    user = User(email="feedback-user@example.com", hashed_password="hash", full_name="User")
    session.add(user)
    await session.flush()

    execution = SessionContext(
        status=EngineStatus.COMPLETED,
        phase=InterviewPhase.FINAL,
        interview_type=InterviewType.TECHNICAL,
        company_name="EPAM",
        target_role="SDE intern",
        questions=[
            SessionQuestion(
                position=0,
                phase=InterviewPhase.INTRODUCTION,
                text="Tell me about yourself.",
                category="behavioral",
                difficulty="easy",
                answered=True,
                answer_transcript="Structured intro with project examples.",
                evaluation=_evaluation(),
            )
        ],
    )
    interview = Interview(
        user_id=user.id,
        role="SDE intern",
        company="EPAM",
        interview_type=InterviewType.TECHNICAL,
        status=InterviewStatus.COMPLETED,
        interview_metadata={
            "company_name": "EPAM",
            "target_role": "SDE intern",
            "interview_type": "technical",
            "has_job_description": False,
            "resume_summary": {
                "skills": ["Python"],
                "technologies": ["FastAPI"],
                "project_names": ["UncDoIt"],
                "experience_titles": ["Intern"],
            },
            "context_sources": ["parsed_resume"],
        },
        interview_plan={
            "focus_areas": ["Python"],
            "question_mix": ["technical_core"],
            "estimated_rounds": 2,
            "follow_up_strategy": "Ask follow-ups.",
            "evaluation_axes": ["clarity"],
        },
        execution_context=execution.model_dump(mode="json"),
    )
    session.add(interview)
    await session.flush()
    return interview, user


async def test_generate_for_interview_persists_feedback(session: AsyncSession) -> None:
    interview, user = await _seed_completed_interview(session)
    service = FeedbackService(
        session,
        InterviewRepository(session),
        FeedbackReportRepository(session),
        FakeFeedbackGenerator(),
    )

    result = await service.generate_for_interview(
        user_id=user.id,
        interview_id=interview.id,
    )

    assert result.generator_name == "fake"
    assert result.learning_roadmap
    fetched = await service.get_for_interview(user_id=user.id, interview_id=interview.id)
    assert fetched.summary == result.summary
    assert fetched.recommendations == result.recommendations
