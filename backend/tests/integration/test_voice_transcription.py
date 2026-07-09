"""Voice transcription integration tests."""

from collections.abc import AsyncGenerator
from io import BytesIO

import pytest
from httpx import AsyncClient

from app.ai.transcription.strategies.fake_transcriber import FakeTranscriber
from app.features.voice.dependencies import get_voice_transcription_service
from app.features.voice.service import VoiceTranscriptionService
from app.features.voice.strategies.noop_refiner import NoOpTranscriptRefiner
from tests.integration.conftest import build_integration_client
from tests.integration.helpers import auth_headers

_REGISTER = {
    "email": "voice-user@example.com",
    "password": "sup3rsecret",
    "full_name": "Voice User",
}
AUDIO_BYTES = b"\x00" * 1024


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async for async_client, _engine in build_integration_client(
        dependency_overrides={
            get_voice_transcription_service: (
                lambda: VoiceTranscriptionService(FakeTranscriber(), NoOpTranscriptRefiner())
            ),
        },
    ):
        yield async_client


async def _auth_headers(client: AsyncClient) -> dict[str, str]:
    return await auth_headers(
        client,
        email=_REGISTER["email"],
        password=_REGISTER["password"],
        full_name=_REGISTER["full_name"],
    )


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
