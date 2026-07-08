"""Interview execution integration tests."""

from collections.abc import AsyncGenerator
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.registry import Base
from app.db.session import get_session
from app.features.evaluation.dependencies import get_answer_evaluator
from app.features.evaluation.schemas import (
    REQUIRED_DIMENSIONS,
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationContext,
)
from app.features.interview.dependencies import get_follow_up_service, get_phase_question_provider
from app.features.interview.execution.question_provider import build_intro_question
from app.features.interview.execution.schemas import InterviewPhase, SessionQuestion
from app.features.interview.follow_up.service import FollowUpService, parse_allowed_phases
from app.features.interview.follow_up.strategies.noop import (
    NoOpClaimExtractor,
    NoOpFollowUpGenerator,
)
from app.features.interview.question_generation.schemas import QuestionGenerationContext
from app.features.resume.dependencies import get_file_storage_service, get_resume_parser
from app.features.resume.parsing.schemas import (
    EducationEntry,
    ExperienceEntry,
    ParsedResume,
    ProjectEntry,
)
from app.features.resume.storage import LocalFileStorageService
from app.main import create_app

MINIMAL_PDF = b"%PDF-1.4\n%%EOF"
_REGISTER = {
    "email": "execution-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Execution User",
}


class FakeResumeParser:
    name = "fake"

    async def parse(self, pdf_bytes: bytes, *, on_progress: object = None) -> ParsedResume:
        return ParsedResume(
            skills=["Python", "FastAPI", "Communication"],
            projects=[ProjectEntry(name="InterviewerAI", description="Mock interviews")],
            experience=[ExperienceEntry(title="Engineer", company="Acme")],
            technologies=["PostgreSQL", "Docker"],
            education=[EducationEntry(institution="Example University", degree="B.Tech")],
            achievements=["Hackathon winner"],
        )


class FakePhaseQuestionProvider:
    async def generate_for_phase(
        self,
        phase: InterviewPhase,
        *,
        company_name: str,
        target_role: str,
        position: int,
        generation_context: QuestionGenerationContext,
    ) -> SessionQuestion:
        if phase == InterviewPhase.INTRODUCTION:
            return build_intro_question(
                company_name=company_name,
                target_role=target_role,
                position=position,
            )
        return SessionQuestion(
            position=position,
            phase=phase,
            text=f"Sample {phase.value} question?",
            category="project",
            difficulty="medium",
            expected_topics=["topic-a"],
            evaluation_rubric=["clarity"],
        )


class FakeAnswerEvaluator:
    name = "fake"

    async def evaluate(self, context: EvaluationContext) -> AnswerEvaluationResult:
        scores = [
            DimensionScore(
                dimension=dim,
                score=7.5,
                rationale="Answer addresses the question with relevant detail.",
            )
            for dim in REQUIRED_DIMENSIONS
        ]
        return AnswerEvaluationResult(
            scores=scores,
            overall_score=7.5,
            strengths=["Clear communication"],
            improvements=["Add concrete metrics"],
            evaluator_name=self.name,
        )


@pytest.fixture
async def client(tmp_path: Path) -> AsyncGenerator[AsyncClient]:
    upload_root = tmp_path / "uploads"
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_session() -> AsyncGenerator[AsyncSession]:
        async with factory() as session:
            yield session

    app: FastAPI = create_app()
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_file_storage_service] = lambda: LocalFileStorageService(
        str(upload_root)
    )
    app.dependency_overrides[get_resume_parser] = lambda: FakeResumeParser()
    app.dependency_overrides[get_phase_question_provider] = lambda: FakePhaseQuestionProvider()
    app.dependency_overrides[get_answer_evaluator] = lambda: FakeAnswerEvaluator()
    app.dependency_overrides[get_follow_up_service] = lambda: FollowUpService(
        NoOpClaimExtractor(),
        NoOpFollowUpGenerator(),
        max_follow_ups_per_answer=1,
        max_follow_ups_per_interview=3,
        allowed_phases=parse_allowed_phases("resume,projects,cs_fundamentals,behavioral"),
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client

    await engine.dispose()


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    await client.post("/api/v1/auth/register", json=_REGISTER)
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": _REGISTER["email"], "password": _REGISTER["password"]},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_interview(client: AsyncClient, headers: dict[str, str]) -> str:
    upload = await client.post(
        "/api/v1/resumes/upload",
        headers=headers,
        files={"file": ("resume.pdf", BytesIO(MINIMAL_PDF), "application/pdf")},
    )
    resume_id = upload.json()["id"]
    await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)

    created = await client.post(
        "/api/v1/interviews/",
        headers=headers,
        json={
            "resume_id": resume_id,
            "company_name": "EPAM",
            "target_role": "SDE intern",
            "interview_type": "behavioral",
        },
    )
    return created.json()["id"]


async def test_execution_start_returns_intro_question(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    interview_id = await _create_interview(client, headers)

    before = await client.get(f"/api/v1/interviews/{interview_id}/execution", headers=headers)
    assert before.status_code == 200
    assert before.json()["status"] == "not_started"

    started = await client.post(
        f"/api/v1/interviews/{interview_id}/execution/start",
        headers=headers,
    )

    assert started.status_code == 200
    body = started.json()
    assert body["status"] == "in_progress"
    assert body["phase"] == "introduction"
    assert body["current_question"]["phase"] == "introduction"
    assert body["session_context"]["awaiting_answer"] is True
    assert body["allowed_transitions"] == []


async def test_submit_answer_advances_to_next_phase(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    interview_id = await _create_interview(client, headers)
    await client.post(f"/api/v1/interviews/{interview_id}/execution/start", headers=headers)

    answered = await client.post(
        f"/api/v1/interviews/{interview_id}/execution/answer",
        headers=headers,
        json={"transcript": "I am interested in backend engineering at EPAM."},
    )

    assert answered.status_code == 200
    body = answered.json()
    assert body["phase"] == "resume"
    assert body["current_question"]["phase"] == "resume"
    assert len(body["previous_questions"]) == 1
    assert body["previous_questions"][0]["answered"] is True
    evaluation = body["previous_questions"][0]["evaluation"]
    assert evaluation is not None
    assert evaluation["overall_score"] == 7.5
    assert len(evaluation["scores"]) == 5
    assert evaluation["evaluator_name"] == "fake"
