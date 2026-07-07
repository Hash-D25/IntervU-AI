"""Select a feedback generator from configuration."""

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.feedback.protocols import FeedbackGenerator
from app.features.feedback.strategies.llm_generator import create_llm_feedback_generator


def create_feedback_generator(settings: Settings) -> FeedbackGenerator:
    if settings.feedback_generator == "llm":
        return create_llm_feedback_generator(settings)
    raise BadRequestError(f"Unsupported feedback generator: {settings.feedback_generator}")
