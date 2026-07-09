"""Shared helpers for integration tests."""

from io import BytesIO

from httpx import AsyncClient

MINIMAL_PDF = b"%PDF-1.4\n%%EOF"


async def auth_headers(
    client: AsyncClient,
    *,
    email: str,
    password: str = "sup3rsecret",
    full_name: str = "Test User",
) -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def upload_resume(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    filename: str = "my-resume.pdf",
    content: bytes = MINIMAL_PDF,
) -> str:
    files = {"file": (filename, BytesIO(content), "application/pdf")}
    response = await client.post("/api/v1/resumes/upload", headers=headers, files=files)
    assert response.status_code == 201
    return response.json()["id"]


async def create_interview(
    client: AsyncClient,
    headers: dict[str, str],
    *,
    resume_id: str,
    interview_type: str = "technical",
    company_name: str = "Acme Corp",
    target_role: str = "Software Engineer",
) -> str:
    response = await client.post(
        "/api/v1/interviews/",
        headers=headers,
        json={
            "resume_id": resume_id,
            "company_name": company_name,
            "target_role": target_role,
            "interview_type": interview_type,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]
