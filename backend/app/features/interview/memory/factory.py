"""Select an interview memory builder from configuration."""

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.interview.memory.builder import NoOpMemoryBuilder, SessionMemoryBuilder
from app.features.interview.memory.protocols import InterviewMemoryBuilder


def create_memory_builder(settings: Settings) -> InterviewMemoryBuilder:
    if settings.interview_memory == "none":
        return NoOpMemoryBuilder()
    if settings.interview_memory == "session":
        return SessionMemoryBuilder(
            max_answers=settings.interview_memory_max_answers,
            excerpt_chars=settings.interview_memory_excerpt_chars,
        )
    raise BadRequestError(f"Unsupported interview memory: {settings.interview_memory}")
