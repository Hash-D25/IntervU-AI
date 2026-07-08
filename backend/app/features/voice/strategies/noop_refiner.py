"""No-op transcript refiner."""

from app.features.voice.schemas import TranscriptionContext


class NoOpTranscriptRefiner:
    name = "none"

    async def refine(self, transcript: str, *, context: TranscriptionContext) -> str:
        return transcript
