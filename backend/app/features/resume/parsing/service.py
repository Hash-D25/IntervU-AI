"""Orchestrate resume parsing: fetch PDF, parse, validate, persist."""

from uuid import UUID

from openai import APIStatusError, RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, NotFoundError, ParseError
from app.features.resume.parsed_models import ResumeParsedProfile
from app.features.resume.parsed_repository import ResumeParsedProfileRepository
from app.features.resume.parsing.progress import ParseProgressCallback
from app.features.resume.parsing.protocols import ResumeParser
from app.features.resume.repository import ResumeRepository
from app.features.resume.storage import FileStorageService


def _failure_message(exc: Exception) -> str:
    if isinstance(exc, RateLimitError):
        return "LLM quota exceeded. Check your OpenAI billing and plan."
    if isinstance(exc, APIStatusError):
        return f"LLM request failed: {exc.message}"
    return "Failed to parse resume"


class ResumeParsingService:
    def __init__(
        self,
        session: AsyncSession,
        resume_repository: ResumeRepository,
        parsed_repository: ResumeParsedProfileRepository,
        storage: FileStorageService,
        parser: ResumeParser,
    ) -> None:
        self._session = session
        self._resumes = resume_repository
        self._parsed = parsed_repository
        self._storage = storage
        self._parser = parser

    async def parse(
        self,
        resume_id: UUID,
        user_id: UUID,
        *,
        on_progress: ParseProgressCallback | None = None,
    ) -> ResumeParsedProfile:
        resume = await self._resumes.get_for_user(resume_id, user_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        stored_path = resume.stored_path

        async def report(stage: str, percent: int, message: str) -> None:
            if on_progress is not None:
                await on_progress(stage, percent, message)

        try:
            await report("fetching", 10, "Downloading resume PDF…")
            pdf_bytes = await self._storage.fetch(stored_path)
            parsed = await self._parser.parse(pdf_bytes, on_progress=on_progress)
            await report("saving", 90, "Saving parsed profile…")
            profile = await self._parsed.upsert_completed(
                resume_id=resume_id,
                parser_name=self._parser.name,
                parsed=parsed,
            )
            await self._session.commit()
            await report("complete", 100, "Parse complete")
            return profile
        except AppError as exc:
            await self._session.rollback()
            await self._record_failure(resume_id, str(exc.message))
            raise
        except Exception as exc:
            await self._session.rollback()
            message = _failure_message(exc)
            await self._record_failure(resume_id, message)
            raise ParseError(message) from exc

    async def get_parsed(self, resume_id: UUID, user_id: UUID) -> ResumeParsedProfile:
        resume = await self._resumes.get_for_user(resume_id, user_id)
        if resume is None:
            raise NotFoundError("Resume not found")
        profile = await self._parsed.get_by_resume_id(resume_id)
        if profile is None:
            raise NotFoundError("Parsed resume profile not found")
        return profile

    async def _record_failure(self, resume_id: UUID, message: str) -> None:
        await self._parsed.upsert_failed(
            resume_id=resume_id,
            parser_name=self._parser.name,
            error_message=message,
        )
        await self._session.commit()
