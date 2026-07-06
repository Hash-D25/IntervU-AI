"""Resume upload integration tests."""

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
from app.features.resume.dependencies import get_file_storage_service
from app.features.resume.storage import LocalFileStorageService
from app.main import create_app

MINIMAL_PDF = b"%PDF-1.4\n%%EOF"
_REGISTER = {
    "email": "resume-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Resume User",
}


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

    def override_storage() -> LocalFileStorageService:
        return LocalFileStorageService(str(upload_root))

    app: FastAPI = create_app()
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_file_storage_service] = override_storage

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


async def test_upload_pdf_stores_metadata_and_file(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    files = {"file": ("my-resume.pdf", BytesIO(MINIMAL_PDF), "application/pdf")}

    response = await client.post("/api/v1/resumes/upload", headers=headers, files=files)

    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "my-resume.pdf"
    assert body["file_size_bytes"] == len(MINIMAL_PDF)
    assert body["stored_path"].startswith("resumes/")


async def test_list_and_get_resume(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    upload = await client.post(
        "/api/v1/resumes/upload",
        headers=headers,
        files={"file": ("resume.pdf", BytesIO(MINIMAL_PDF), "application/pdf")},
    )
    resume_id = upload.json()["id"]

    listed = await client.get("/api/v1/resumes/", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = await client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["id"] == resume_id


async def test_upload_without_auth_is_rejected(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.pdf", BytesIO(MINIMAL_PDF), "application/pdf")},
    )
    assert response.status_code == 401


async def test_upload_non_pdf_is_rejected(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    response = await client.post(
        "/api/v1/resumes/upload",
        headers=headers,
        files={"file": ("notes.txt", BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400


async def test_delete_resume(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    upload = await client.post(
        "/api/v1/resumes/upload",
        headers=headers,
        files={"file": ("resume.pdf", BytesIO(MINIMAL_PDF), "application/pdf")},
    )
    resume_id = upload.json()["id"]

    deleted = await client.delete(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert deleted.status_code == 204

    missing = await client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert missing.status_code == 404
