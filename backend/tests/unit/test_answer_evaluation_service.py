"""Answer evaluation service unit tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.registry import Base
from app.features.evaluation.repository import AnswerEvaluationRepository
from app.features.evaluation.schemas import (
    REQUIRED_DIMENSIONS,
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationContext,
)
from app.features.evaluation.service import AnswerEvaluationService
from app.features.interview.models import Answer, Interview, InterviewStatus, Question, QuestionKind
from app.features.interview.planning.schemas import InterviewType
from app.features.interview.repository import InterviewRepository
from app.features.user.models import User


class FakeAnswerEvaluator:
    name = "fake"

    async def evaluate(self, context: EvaluationContext) -> AnswerEvaluationResult:
        scores = [
            DimensionScore(
                dimension=dim,
                score=8.0,
                rationale=f"Good coverage of {dim.value}.",
            )
            for dim in REQUIRED_DIMENSIONS
        ]
        return AnswerEvaluationResult(
            scores=scores,
            overall_score=8.0,
            strengths=["Clear explanation"],
            improvements=["Add more examples"],
            evaluator_name=self.name,
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


async def _seed_answer(session: AsyncSession) -> tuple[Interview, Question, Answer]:
    user = User(email="eval-user@example.com", hashed_password="hash", full_name="Eval User")
    session.add(user)
    await session.flush()

    interview = Interview(
        user_id=user.id,
        role="SDE intern",
        company="EPAM",
        interview_type=InterviewType.TECHNICAL,
        status=InterviewStatus.IN_PROGRESS,
        interview_metadata={
            "company_name": "EPAM",
            "target_role": "SDE intern",
            "interview_type": "technical",
            "has_job_description": False,
            "resume_summary": {
                "skills": ["Python"],
                "technologies": ["FastAPI"],
                "project_names": ["InterviewerAI"],
                "experience_titles": ["Intern"],
            },
            "context_sources": ["parsed_resume"],
        },
        interview_plan={
            "focus_areas": ["Python"],
            "question_mix": ["technical_core"],
            "estimated_rounds": 2,
            "follow_up_strategy": "Ask follow-ups.",
            "evaluation_axes": ["clarity", "depth"],
        },
    )
    session.add(interview)
    await session.flush()

    question = Question(
        interview_id=interview.id,
        position=0,
        text="Explain your authentication design.",
        kind=QuestionKind.TECHNICAL,
    )
    session.add(question)
    await session.flush()

    answer = Answer(question_id=question.id, transcript="I used JWT with FastAPI dependencies.")
    session.add(answer)
    await session.flush()
    return interview, question, answer


async def test_evaluate_and_persist_stores_scores(session: AsyncSession) -> None:
    interview, question, answer = await _seed_answer(session)
    service = AnswerEvaluationService(
        session,
        AnswerEvaluationRepository(session),
        InterviewRepository(session),
        FakeAnswerEvaluator(),
    )
    context = EvaluationContext(
        question_text=question.text,
        answer_transcript=answer.transcript,
        category="cs_fundamentals",
        phase="cs_fundamentals",
        difficulty="medium",
        expected_topics=["authentication"],
        evaluation_rubric=["clarity"],
        company_name="EPAM",
        target_role="SDE intern",
    )

    result = await service.evaluate_and_persist(answer_id=answer.id, context=context)

    assert result.overall_score == 8.0
    assert len(result.scores) == 5
    fetched = await service.get_for_question(
        user_id=interview.user_id,
        interview_id=interview.id,
        question_id=question.id,
    )
    assert fetched.overall_score == 8.0
    assert fetched.evaluator_name == "fake"
