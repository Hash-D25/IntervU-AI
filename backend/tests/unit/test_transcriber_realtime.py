"""Realtime (live chunk stream) transcription contract tests."""

from collections.abc import AsyncIterator

import pytest

from app.ai.transcription.base import Transcriber
from app.ai.transcription.strategies.fake_transcriber import FakeTranscriber
from app.ai.transcription.strategies.whisper_transcriber import WhisperTranscriber
from app.core.exceptions import BadRequestError


async def _audio_chunks() -> AsyncIterator[bytes]:
    for _ in range(3):
        yield b"\x00" * 16


def _whisper() -> WhisperTranscriber:
    return WhisperTranscriber(
        model_name="base",
        language=None,
        device="cpu",
        compute_type="int8",
        enable_vad=True,
        return_word_timestamps=False,
        beam_size=5,
    )


async def test_fake_transcriber_realtime_yields_partial_then_final() -> None:
    chunks = [chunk async for chunk in FakeTranscriber().transcribe_realtime(_audio_chunks())]
    assert chunks
    assert chunks[-1].is_final is True
    assert any(not chunk.is_final for chunk in chunks)


async def test_fake_transcriber_realtime_handles_empty_stream() -> None:
    async def _empty() -> AsyncIterator[bytes]:
        return
        yield b""  # pragma: no cover - makes this an async generator

    chunks = [chunk async for chunk in FakeTranscriber().transcribe_realtime(_empty())]
    assert chunks
    assert chunks[-1].is_final is True


def test_whisper_satisfies_extended_transcriber_protocol() -> None:
    assert isinstance(_whisper(), Transcriber)


async def test_whisper_realtime_stub_raises_on_iteration() -> None:
    with pytest.raises(BadRequestError, match="realtime"):
        async for _ in _whisper().transcribe_realtime(_audio_chunks()):
            pass
