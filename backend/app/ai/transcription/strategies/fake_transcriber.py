"""Deterministic transcriber for tests and local development."""

from collections.abc import AsyncIterator

from app.ai.transcription.base import ProcessedAudio
from app.ai.transcription.schemas import TranscriptionChunk, TranscriptionResult


class FakeTranscriber:
    name = "fake"
    supports_streaming = True

    async def transcribe(self, audio: ProcessedAudio) -> TranscriptionResult:
        transcript = "Transcribed answer from microphone input."
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
        words = result.transcript.split()
        if not words:
            yield TranscriptionChunk(text=result.transcript, is_final=True)
            return
        mid = max(1, len(words) // 2)
        partial = " ".join(words[:mid])
        final = " ".join(words[mid:])
        yield TranscriptionChunk(text=f"{partial} ", is_final=False)
        yield TranscriptionChunk(text=final, is_final=True)
