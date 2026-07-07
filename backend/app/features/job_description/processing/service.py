"""Orchestrate job description analysis."""

from openai import APIStatusError, RateLimitError

from app.core.exceptions import ParseError
from app.features.job_description.processing.input import (
    extract_job_description_text_from_pdf,
    normalize_job_description_text,
)
from app.features.job_description.processing.protocols import JobDescriptionAnalyzer
from app.features.job_description.processing.schemas import ParsedJobDescription


def _failure_message(exc: Exception) -> str:
    if isinstance(exc, RateLimitError):
        return "LLM quota exceeded. Check your provider billing and plan."
    if isinstance(exc, APIStatusError):
        return f"LLM request failed: {exc.message}"
    return "Failed to analyze job description"


class JobDescriptionProcessingService:
    def __init__(self, analyzer: JobDescriptionAnalyzer) -> None:
        self._analyzer = analyzer

    @property
    def analyzer_name(self) -> str:
        return self._analyzer.name

    async def analyze(self, text: str) -> ParsedJobDescription:
        return await self._analyze_text(normalize_job_description_text(text))

    async def analyze_pdf(self, pdf_bytes: bytes) -> ParsedJobDescription:
        return await self._analyze_text(extract_job_description_text_from_pdf(pdf_bytes))

    async def _analyze_text(self, text: str) -> ParsedJobDescription:
        try:
            return await self._analyzer.analyze(text)
        except ParseError:
            raise
        except Exception as exc:
            raise ParseError(_failure_message(exc)) from exc
