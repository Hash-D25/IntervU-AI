"""Voice transcription integration tests."""

from collections.abc import AsyncGenerator
from io import BytesIO

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.ai.transcription.strategies.fake_transcriber import FakeTranscriber
from app.db.registry import Base
from app.db.session import get_session
from app.features.voice.dependencies import get_voice_transcription_service
from app.features.voice.service import VoiceTranscriptionService
from app.features.voice.strategies.noop_refiner import NoOpTranscriptRefiner
from app.main import create_app

_REGISTER = {
    "email": "voice-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Voice User",
}
AUDIO_BYTES = b"\x00" * 1024


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
    app.dependency_overrides[get_voice_transcription_service] = (
        lambda: VoiceTranscriptionService(FakeTranscriber(), NoOpTranscriptRefiner())
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


async def test_transcribe_audio_returns_transcript(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    response = await client.post(
        "/api/v1/voice/transcribe",
        headers=headers,
        files={"file": ("answer.webm", BytesIO(AUDIO_BYTES), "audio/webm")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["transcriber_name"] == "fake"
    assert body["transcript"]


async def test_transcribe_stream_returns_sse_chunks(client: AsyncClient) -> None:
    headers = await _auth_headers(client)
    response = await client.post(
        "/api/v1/voice/transcribe/stream",
        headers=headers,
        files={"file": ("answer.webm", BytesIO(AUDIO_BYTES), "audio/webm")},
    )
    assert response.status_code == 200
    text = response.text
    assert "data:" in text
    assert '"stage":"done"' in text.replace(" ", "")
