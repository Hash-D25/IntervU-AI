"""Resume parsing integration tests with a fake parser (no live LLM calls)."""

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
    "email": "parser-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Parser User",
}


class FakeResumeParser:
    name = "fake"

    async def parse(
        self,
        pdf_bytes: bytes,
        *,
        on_progress: object = None,
    ) -> ParsedResume:
        return ParsedResume(
            skills=["Python", "FastAPI"],
            projects=[ProjectEntry(name="InterviewerAI", description="Mock interviews")],
            experience=[ExperienceEntry(title="Engineer", company="Acme")],
            technologies=["PostgreSQL"],
            education=[EducationEntry(institution="Example University", degree="B.Tech")],
            achievements=["Best project award"],
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


async def test_parse_resume_returns_structured_profile(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    resume_id = await _upload_resume(client, headers)

    response = await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["parse_status"] == "completed"
    assert "Python" in body["skills"]
    assert body["projects"][0]["name"] == "InterviewerAI"


async def test_get_parsed_before_parse_returns_not_found(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    resume_id = await _upload_resume(client, headers)

    response = await client.get(f"/api/v1/resumes/{resume_id}/parsed", headers=headers)
    assert response.status_code == 404


async def test_reparse_overwrites_existing_profile(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    resume_id = await _upload_resume(client, headers)

    first = await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)
    second = await client.post(f"/api/v1/resumes/{resume_id}/parse", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["parser_name"] == "fake"
