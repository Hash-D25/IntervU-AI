"""Dashboard API integration tests."""

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
    "email": "dashboard-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Dashboard User",
}


class FakeResumeParser:
    name = "fake"

    async def parse(self, pdf_bytes: bytes, *, on_progress: object = None) -> ParsedResume:
        return ParsedResume(
            skills=["Python"],
            projects=[ProjectEntry(name="UncDoIt", description="Docs tool")],
            experience=[ExperienceEntry(title="Intern", company="Startup")],
            technologies=["FastAPI"],
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


async def _create_interview(client: AsyncClient, headers: dict[str, str]) -> str:
    upload = await client.post(
        "/api/v1/resumes/upload",
        headers=headers,
        files={"file": ("resume.pdf", BytesIO(MINIMAL_PDF), "application/pdf")},
    )
    resume_id = upload.json()["id"]
    await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)
    create = await client.post(
        "/api/v1/interviews/",
        headers=headers,
        json={
            "resume_id": resume_id,
            "company_name": "EPAM",
            "target_role": "SDE intern",
            "interview_type": "technical",
        },
    )
    return create.json()["id"]


@pytest.mark.asyncio
async def test_dashboard_and_interview_list(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    interview_id = await _create_interview(client, headers)

    list_response = await client.get("/api/v1/interviews/", headers=headers)
    assert list_response.status_code == 200
    interviews = list_response.json()
    assert len(interviews) == 1
    assert interviews[0]["id"] == interview_id
    assert interviews[0]["company_name"] == "EPAM"

    dashboard = await client.get("/api/v1/dashboard/", headers=headers)
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["total_interviews"] == 1
    assert len(body["interview_history"]) == 1
    assert body["interview_history"][0]["target_role"] == "SDE intern"
    assert body["category_scores"] == []
    assert body["progress_over_time"] == []
