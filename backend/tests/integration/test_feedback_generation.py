"""Feedback generation integration tests."""

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
from app.features.feedback.dependencies import get_feedback_generator
from app.features.feedback.schemas import FeedbackContext, FeedbackResult
from app.features.interview.dependencies import get_phase_question_provider
from app.features.interview.execution.question_provider import build_intro_question
from app.features.interview.execution.schemas import InterviewPhase, SessionQuestion
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
    "email": "feedback-api-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Feedback User",
}


class FakeResumeParser:
    name = "fake"

    async def parse(self, pdf_bytes: bytes, *, on_progress: object = None) -> ParsedResume:
        return ParsedResume(
            skills=["Python", "FastAPI"],
            projects=[ProjectEntry(name="UncDoIt", description="Undo/redo for docs")],
            experience=[ExperienceEntry(title="Intern", company="Startup")],
            technologies=["PostgreSQL"],
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
                score=8.0,
                rationale="Solid answer with relevant detail.",
            )
            for dim in REQUIRED_DIMENSIONS
        ]
        return AnswerEvaluationResult(
            scores=scores,
            overall_score=8.0,
            strengths=["Clear communication"],
            improvements=["Add more metrics"],
            evaluator_name=self.name,
        )


class FakeFeedbackGenerator:
    name = "fake"

    async def generate(self, context: FeedbackContext) -> FeedbackResult:
        return FeedbackResult(
            summary="Strong interview with clear communication and good project examples.",
            strengths=["Clear communication", "Relevant project storytelling"],
            weaknesses=["Could deepen technical tradeoff explanations"],
            recommendations=["Practice system design out loud twice per week"],
            learning_roadmap=[
                "Week 1: review authentication and authorization patterns",
                "Week 2: mock architecture discussions",
            ],
            overall_score=context.overall_average_score,
            generator_name=self.name,
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
    app.dependency_overrides[get_feedback_generator] = lambda: FakeFeedbackGenerator()

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


async def _create_interview_with_answer(client: AsyncClient, headers: dict[str, str]) -> str:
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
            "interview_type": "technical",
        },
    )
    interview_id = created.json()["id"]
    await client.post(f"/api/v1/interviews/{interview_id}/execution/start", headers=headers)
    await client.post(
        f"/api/v1/interviews/{interview_id}/execution/answer",
        headers=headers,
        json={"transcript": "I am a backend engineer with FastAPI and PostgreSQL experience."},
    )
    return interview_id


async def test_generate_feedback_returns_json_report(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    interview_id = await _create_interview_with_answer(client, headers)

    generated = await client.post(
        f"/api/v1/interviews/{interview_id}/feedback/generate",
        headers=headers,
    )

    assert generated.status_code == 201
    body = generated.json()
    assert body["generator_name"] == "fake"
    assert body["strengths"]
    assert body["weaknesses"]
    assert body["recommendations"]
    assert body["learning_roadmap"]
    assert body["overall_score"] == 8.0

    fetched = await client.get(
        f"/api/v1/interviews/{interview_id}/feedback",
        headers=headers,
    )
    assert fetched.status_code == 200
    assert fetched.json()["summary"] == body["summary"]
    assert fetched.json()["recommendations"] == body["recommendations"]
