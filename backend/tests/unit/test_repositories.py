"""Repository CRUD + relationship tests against in-memory SQLite.

These validate repository *logic* (not Postgres-specific behavior). A
Postgres-backed integration suite is added in a later iteration.
"""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.registry import Base
from app.features.feedback.models import FeedbackReport
from app.features.feedback.repository import FeedbackReportRepository
from app.features.interview.models import Answer, Interview, InterviewStatus, Question, QuestionKind
from app.features.interview.repository import (
    AnswerRepository,
    InterviewRepository,
    QuestionRepository,
)
from app.features.user.models import User
from app.features.user.repository import UserRepository


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session
    await engine.dispose()


async def _make_user(session: AsyncSession, email: str = "candidate@example.com") -> User:
    return await UserRepository(session).add(
        User(email=email, full_name="Test Candidate", hashed_password="x")
    )


async def test_user_add_get_and_lookup_by_email(session: AsyncSession) -> None:
    repo = UserRepository(session)
    created = await repo.add(User(email="a@example.com", full_name="A", hashed_password="x"))

    assert created.id is not None
    assert created.created_at is not None

    assert (await repo.get(created.id)) is not None
    assert (await repo.get_by_email("a@example.com")) is not None
    assert (await repo.get_by_email("missing@example.com")) is None


async def test_interview_question_answer_relationships(session: AsyncSession) -> None:
    user = await _make_user(session)
    interview = await InterviewRepository(session).add(
        Interview(user_id=user.id, role="Backend Engineer", status=InterviewStatus.CREATED)
    )
    question = await QuestionRepository(session).add(
        Question(
            interview_id=interview.id,
            position=1,
            text="Why Redis?",
            kind=QuestionKind.TECHNICAL,
        )
    )
    answer = await AnswerRepository(session).add(
        Answer(question_id=question.id, transcript="For low-latency caching.")
    )

    assert (await AnswerRepository(session).get_for_question(question.id)) == answer

    await session.refresh(interview, ["questions"])
    assert [q.id for q in interview.questions] == [question.id]


async def test_list_interviews_for_user(session: AsyncSession) -> None:
    user = await _make_user(session)
    repo = InterviewRepository(session)
    await repo.add(Interview(user_id=user.id, role="Role A"))
    await repo.add(Interview(user_id=user.id, role="Role B"))

    interviews = await repo.list_for_user(user.id)
    assert len(interviews) == 2


async def test_feedback_report_for_interview(session: AsyncSession) -> None:
    user = await _make_user(session)
    interview = await InterviewRepository(session).add(Interview(user_id=user.id, role="Role"))
    repo = FeedbackReportRepository(session)
    await repo.add(
        FeedbackReport(
            interview_id=interview.id,
            summary="Solid fundamentals.",
            strengths=["clear communication"],
            weaknesses=["shallow on caching"],
            suggestions=["study eviction policies"],
            roadmap=["week 1: Redis internals"],
            overall_score=7.5,
        )
    )

    report = await repo.get_for_interview(interview.id)
    assert report is not None
    assert report.strengths == ["clear communication"]
    assert report.overall_score == 7.5


async def test_cascade_delete_removes_children(session: AsyncSession) -> None:
    user = await _make_user(session)
    interview = await InterviewRepository(session).add(Interview(user_id=user.id, role="Role"))
    question = await QuestionRepository(session).add(
        Question(interview_id=interview.id, position=1, text="Q", kind=QuestionKind.TECHNICAL)
    )

    await session.refresh(interview, ["questions"])
    await InterviewRepository(session).delete(interview)

    assert (await QuestionRepository(session).get(question.id)) is None
