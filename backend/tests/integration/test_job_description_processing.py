"""Job description analysis integration tests with a fake analyzer (no live LLM)."""

from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.registry import Base
from app.db.session import get_session
from app.features.job_description.dependencies import get_job_description_analyzer
from app.features.job_description.processing.schemas import ParsedJobDescription
from app.features.job_description.processing.seniority import SeniorityLevel
from app.main import create_app

SAMPLE_JD = """
Senior Backend Engineer

Requirements:
- Python, FastAPI, PostgreSQL
- AWS and Docker experience

Responsibilities:
- Build scalable REST APIs
- Collaborate with product and frontend teams
"""

_REGISTER = {
    "email": "jd-user@example.com",
    "password": "sup3rsecret",
    "full_name": "JD User",
}


class FakeJobDescriptionAnalyzer:
    name = "fake"

    async def analyze(self, text: str) -> ParsedJobDescription:
        assert "Senior Backend Engineer" in text
        return ParsedJobDescription(
            skills=["Python", "Communication"],
            technologies=["FastAPI", "PostgreSQL", "AWS"],
            responsibilities=["Build scalable REST APIs"],
            seniority_level=SeniorityLevel.SENIOR,
        )


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
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
    app.dependency_overrides[get_job_description_analyzer] = lambda: FakeJobDescriptionAnalyzer()

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


async def test_analyze_job_description_returns_structured_json(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    response = await client.post(
        "/api/v1/job-descriptions/analyze",
        headers=headers,
        json={"text": SAMPLE_JD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["analyzer_name"] == "fake"
    assert body["seniority_level"] == "senior"
    assert "Python" in body["skills"]
    assert "FastAPI" in body["technologies"]
    assert body["responsibilities"][0] == "Build scalable REST APIs"


async def test_analyze_job_description_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/job-descriptions/analyze",
        json={"text": SAMPLE_JD},
    )
    assert response.status_code == 401


async def test_analyze_job_description_pdf(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.features.job_description.processing.service.extract_job_description_text_from_pdf",
        lambda _pdf_bytes: SAMPLE_JD.strip(),
    )
    headers = await _auth_headers(client)
    response = await client.post(
        "/api/v1/job-descriptions/analyze/pdf",
        headers=headers,
        files={"file": ("jd.pdf", b"%PDF-1.4\n%%EOF", "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["analyzer_name"] == "fake"
    assert "Python" in body["skills"]
    assert "Senior Backend Engineer" in body["extracted_text"]


async def test_analyze_job_description_pdf_rejects_non_pdf(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    response = await client.post(
        "/api/v1/job-descriptions/analyze/pdf",
        headers=headers,
        files={"file": ("jd.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400
