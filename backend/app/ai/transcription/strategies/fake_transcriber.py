"""Deterministic transcriber for tests and local development."""

from collections.abc import AsyncIterator

from app.ai.transcription.base import ProcessedAudio
from app.ai.transcription.schemas import TranscriptionChunk, TranscriptionResult

_SCRIPTED_TRANSCRIPT = "Transcribed answer from microphone input."


def _scripted_chunks(transcript: str) -> list[TranscriptionChunk]:
    """Split a transcript into a deterministic partial + final chunk pair."""
    words = transcript.split()
    if not words:
        return [TranscriptionChunk(text=transcript, is_final=True)]
    mid = max(1, len(words) // 2)
    partial = " ".join(words[:mid])
    final = " ".join(words[mid:])
    return [
        TranscriptionChunk(text=f"{partial} ", is_final=False),
        TranscriptionChunk(text=final, is_final=True),
    ]


class FakeTranscriber:
    name = "fake"
    supports_streaming = True

    async def transcribe(self, audio: ProcessedAudio) -> TranscriptionResult:
        transcript = _SCRIPTED_TRANSCRIPT
        if audio.filename:
            transcript = f"Transcribed answer from {audio.filename}."
        return TranscriptionResult(
            transcript=transcript,
            language="en",
            duration_ms=1_500,
            confidence=0.99,
            chunks=[TranscriptionChunk(text=transcript, is_final=True)],
            transcriber_name=self.name,
            is_final=True,
        )

    async def transcribe_stream(
        self,
        audio: ProcessedAudio,
    ) -> AsyncIterator[TranscriptionChunk]:
        result = await self.transcribe(audio)
        for chunk in _scripted_chunks(result.transcript):
            yield chunk

    async def transcribe_realtime(
        self,
        chunks: AsyncIterator[bytes],
    ) -> AsyncIterator[TranscriptionChunk]:
        async for _ in chunks:
            pass
        for chunk in _scripted_chunks(_SCRIPTED_TRANSCRIPT):
            yield chunk
