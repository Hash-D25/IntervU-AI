"""Provider-agnostic speech-to-text contract."""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.ai.transcription.schemas import TranscriptionChunk, TranscriptionResult


@dataclass(frozen=True, slots=True)
class ProcessedAudio:
    """Normalized audio payload produced by the voice feature layer."""

    content: bytes
    content_type: str
    filename: str
    initial_prompt: str | None = None


@runtime_checkable
class Transcriber(Protocol):
    """Speech-to-text engine. Interview logic never depends on a concrete SDK."""

    name: str
    supports_streaming: bool

    async def transcribe(self, audio: ProcessedAudio) -> TranscriptionResult: ...

    def transcribe_stream(
        self,
        audio: ProcessedAudio,
    ) -> AsyncIterator[TranscriptionChunk]: ...

    def transcribe_realtime(
        self,
        chunks: AsyncIterator[bytes],
    ) -> AsyncIterator[TranscriptionChunk]: ...
