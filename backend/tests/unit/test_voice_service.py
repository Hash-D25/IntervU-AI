"""Voice transcription service unit tests."""

import pytest

from app.ai.transcription.base import ProcessedAudio
from app.ai.transcription.strategies.fake_transcriber import FakeTranscriber
from app.features.voice.service import VoiceTranscriptionService
from app.features.voice.strategies.noop_refiner import NoOpTranscriptRefiner


@pytest.fixture
def service() -> VoiceTranscriptionService:
    return VoiceTranscriptionService(FakeTranscriber(), NoOpTranscriptRefiner())


@pytest.mark.asyncio
async def test_transcribe_returns_transcript(service: VoiceTranscriptionService) -> None:
    audio = ProcessedAudio(
        content=b"\x00" * 512,
        content_type="audio/webm",
        filename="answer.webm",
    )
    result = await service.transcribe(audio)
    assert result.transcriber_name == "fake"
    assert "Transcribed answer" in result.transcript


@pytest.mark.asyncio
async def test_transcribe_stream_yields_chunks(service: VoiceTranscriptionService) -> None:
    audio = ProcessedAudio(
        content=b"\x00" * 512,
        content_type="audio/webm",
        filename="answer.webm",
    )
    chunks = [chunk async for chunk in service.transcribe_stream(audio)]
    assert chunks
    assert chunks[-1].is_final is True
