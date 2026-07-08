"""Select a transcript refiner from configuration."""

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.voice.protocols import TranscriptRefiner
from app.features.voice.strategies.llm_refiner import create_llm_transcript_refiner
from app.features.voice.strategies.noop_refiner import NoOpTranscriptRefiner


def create_transcript_refiner(settings: Settings) -> TranscriptRefiner:
    if settings.transcript_refiner == "llm":
        return create_llm_transcript_refiner(settings)
    if settings.transcript_refiner == "none":
        return NoOpTranscriptRefiner()
    raise BadRequestError(f"Unsupported transcript refiner: {settings.transcript_refiner}")
