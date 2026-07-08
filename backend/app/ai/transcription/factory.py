"""Select a speech-to-text engine from configuration."""

from app.ai.transcription.base import Transcriber
from app.ai.transcription.strategies.fake_transcriber import FakeTranscriber
from app.ai.transcription.strategies.whisper_transcriber import create_whisper_transcriber
from app.core.config import Settings
from app.core.exceptions import BadRequestError


def create_transcriber(settings: Settings) -> Transcriber:
    if settings.transcriber == "whisper":
        return create_whisper_transcriber(settings)
    if settings.transcriber == "fake":
        return FakeTranscriber()
    raise BadRequestError(f"Unsupported transcriber: {settings.transcriber}")
