"""Deterministic synthesizer for tests and local development."""

import io
import wave
from collections.abc import AsyncIterator

from app.ai.synthesis.base import AudioChunk, SynthesizedAudio

_SAMPLE_RATE = 24_000
_CONTENT_TYPE = "audio/wav"
_SILENCE_MS = 300


def _build_silent_wav(sample_rate: int, duration_ms: int) -> bytes:
    """Build a valid, tiny mono 16-bit PCM WAV containing only silence."""
    frame_count = int(sample_rate * duration_ms / 1000)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"\x00\x00" * frame_count)
    return buffer.getvalue()


class FakeSynthesizer:
    name = "fake"
    supports_streaming = True

    async def synthesize(self, text: str, *, voice: str | None = None) -> SynthesizedAudio:
        return SynthesizedAudio(
            content=_build_silent_wav(_SAMPLE_RATE, _SILENCE_MS),
            content_type=_CONTENT_TYPE,
            sample_rate=_SAMPLE_RATE,
        )

    async def synthesize_stream(self, text: str) -> AsyncIterator[AudioChunk]:
        audio = await self.synthesize(text)
        midpoint = max(1, len(audio.content) // 2)
        yield AudioChunk(
            content=audio.content[:midpoint],
            content_type=audio.content_type,
            sample_rate=audio.sample_rate,
            is_final=False,
        )
        yield AudioChunk(
            content=audio.content[midpoint:],
            content_type=audio.content_type,
            sample_rate=audio.sample_rate,
            is_final=True,
        )
