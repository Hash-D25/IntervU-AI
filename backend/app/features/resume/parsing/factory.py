"""Select a resume parsing strategy from configuration."""

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.resume.parsing.protocols import ResumeParser
from app.features.resume.parsing.strategies.hybrid_parser import create_hybrid_resume_parser
from app.features.resume.parsing.strategies.llm_parser import create_llm_resume_parser


def create_resume_parser(settings: Settings) -> ResumeParser:
    if settings.resume_parser == "llm":
        return create_llm_resume_parser(settings)
    if settings.resume_parser == "hybrid":
        return create_hybrid_resume_parser(settings)
    raise BadRequestError(f"Unsupported resume parser: {settings.resume_parser}")
