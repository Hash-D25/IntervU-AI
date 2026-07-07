"""Select a job description analysis strategy from configuration."""

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.job_description.processing.protocols import JobDescriptionAnalyzer
from app.features.job_description.processing.strategies.llm_analyzer import (
    create_llm_job_description_analyzer,
)


def create_job_description_analyzer(settings: Settings) -> JobDescriptionAnalyzer:
    if settings.job_description_analyzer == "llm":
        return create_llm_job_description_analyzer(settings)
    raise BadRequestError(
        f"Unsupported job description analyzer: {settings.job_description_analyzer}"
    )
