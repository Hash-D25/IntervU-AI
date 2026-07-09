"""End-to-end auth flow against in-memory SQLite.

The ``get_session`` dependency is overridden to use a StaticPool SQLite engine so
the in-memory database persists across requests within a test.
"""

from collections.abc import AsyncGenerator
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from tests.integration.conftest import build_integration_client

_REGISTER_PAYLOAD = {
    "email": "candidate@example.com",
    "password": "sup3rsecret",
    "full_name": "Test Candidate",
}


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async for async_client, _engine in build_integration_client(
        settings_overrides={"google_client_id": "test-google-client-id"},
    ):
        yield async_client


async def _register_and_login(client: AsyncClient) -> dict[str, str]:
    await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": _REGISTER_PAYLOAD["email"], "password": _REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    return response.json()


async def test_register_returns_user_without_password(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == _REGISTER_PAYLOAD["email"]
    assert "password" not in body
    assert "hashed_password" not in body


async def test_duplicate_registration_conflicts(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)
    response = await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)

    assert response.status_code == 409


async def test_login_with_wrong_password_is_unauthorized(client: AsyncClient) -> None:
    await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": _REGISTER_PAYLOAD["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401


async def test_me_returns_current_user_with_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == _REGISTER_PAYLOAD["email"]


async def test_me_without_token_is_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_refresh_rotates_and_invalidates_old_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    old_refresh = tokens["refresh_token"]

    rotated = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != old_refresh

    reused = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reused.status_code == 401


async def test_logout_revokes_refresh_token(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)

    logout = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}
    )
    assert logout.status_code == 204

    reused = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert reused.status_code == 401


_GOOGLE_CLAIMS = {
    "sub": "google-user-123",
    "email": "google.user@example.com",
    "email_verified": True,
    "name": "Google User",
    "iss": "accounts.google.com",
}


@patch("app.features.auth.service.verify_google_id_token", return_value=_GOOGLE_CLAIMS)
async def test_google_login_creates_user_and_returns_tokens(
    _mock_verify: object, client: AsyncClient
) -> None:
    response = await client.post("/api/v1/auth/google", json={"id_token": "fake-google-token"})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == _GOOGLE_CLAIMS["email"]


@patch(
    "app.features.auth.service.verify_google_id_token",
    return_value={
        **_GOOGLE_CLAIMS,
        "email": _REGISTER_PAYLOAD["email"],
        "name": _REGISTER_PAYLOAD["full_name"],
    },
)
async def test_google_login_links_existing_password_account(
    _mock_verify: object, client: AsyncClient
) -> None:
    await client.post("/api/v1/auth/register", json=_REGISTER_PAYLOAD)

    response = await client.post(
        "/api/v1/auth/google",
        json={"id_token": "fake-google-token"},
    )
    assert response.status_code == 200

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {response.json()['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == _REGISTER_PAYLOAD["email"]
