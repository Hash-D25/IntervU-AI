"""Interview creation integration tests."""

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
    "email": "interview-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Interview User",
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


async def _upload_resume(client: AsyncClient, headers: dict[str, str]) -> str:
    upload = await client.post(
        "/api/v1/resumes/upload",
        headers=headers,
        files={"file": ("resume.pdf", BytesIO(MINIMAL_PDF), "application/pdf")},
    )
    assert upload.status_code == 201
    return upload.json()["id"]


async def test_create_interview_returns_session_metadata(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    resume_id = await _upload_resume(client, headers)
    await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)

    response = await client.post(
        "/api/v1/interviews/",
        headers=headers,
        json={
            "resume_id": resume_id,
            "company_name": "EPAM",
            "target_role": "AI-Native Software Engineering Intern",
            "interview_type": "mixed",
            "job_description": (
                "Intern role focused on AI-native engineering and strong coding "
                "fundamentals."
            ),
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["company_name"] == "EPAM"
    assert body["target_role"] == "AI-Native Software Engineering Intern"
    assert body["interview_type"] == "mixed"
    assert body["status"] == "created"
    assert body["session_state"]["current"] == "ready"
    assert "parsed_resume" in body["interview_metadata"]["context_sources"]
    assert "job_description" in body["interview_metadata"]["context_sources"]
    assert body["interview_plan"]["focus_areas"]


async def test_create_interview_requires_parsed_resume(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    resume_id = await _upload_resume(client, headers)

    response = await client.post(
        "/api/v1/interviews/",
        headers=headers,
        json={
            "resume_id": resume_id,
            "company_name": "EPAM",
            "target_role": "Intern",
            "interview_type": "technical",
        },
    )

    assert response.status_code == 400


async def test_get_interview_returns_created_session(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    resume_id = await _upload_resume(client, headers)
    await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)

    created = await client.post(
        "/api/v1/interviews/",
        headers=headers,
        json={
            "resume_id": resume_id,
            "company_name": "Acme",
            "target_role": "Backend Engineer",
            "interview_type": "technical",
        },
    )
    interview_id = created.json()["id"]

    fetched = await client.get(f"/api/v1/interviews/{interview_id}", headers=headers)

    assert fetched.status_code == 200
    assert fetched.json()["id"] == interview_id
