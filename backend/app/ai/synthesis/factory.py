"""Select a text-to-speech engine from configuration."""

from app.ai.synthesis.base import SpeechSynthesizer
from app.ai.synthesis.strategies.fake_synthesizer import FakeSynthesizer
from app.core.config import Settings
from app.core.exceptions import BadRequestError


def create_synthesizer(settings: Settings) -> SpeechSynthesizer:
    if settings.synthesizer == "fake":
        return FakeSynthesizer()
    raise BadRequestError(f"Unsupported synthesizer: {settings.synthesizer}")
