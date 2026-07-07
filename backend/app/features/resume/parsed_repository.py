"""Persistence for parsed resume profiles."""

from uuid import UUID

from sqlalchemy import select

from app.db.repository import BaseRepository
from app.features.resume.parsed_models import ParseStatus, ResumeParsedProfile
from app.features.resume.parsing.schemas import ParsedResume


class ResumeParsedProfileRepository(BaseRepository[ResumeParsedProfile]):
    model = ResumeParsedProfile

    async def get_by_resume_id(self, resume_id: UUID) -> ResumeParsedProfile | None:
        result = await self.session.execute(
            select(ResumeParsedProfile).where(ResumeParsedProfile.resume_id == resume_id)
        )
        return result.scalar_one_or_none()

    async def upsert_completed(
        self,
        *,
        resume_id: UUID,
        parser_name: str,
        parsed: ParsedResume,
    ) -> ResumeParsedProfile:
        profile = await self.get_by_resume_id(resume_id)
        if profile is None:
            profile = ResumeParsedProfile(resume_id=resume_id, parser_name=parser_name)
            self.session.add(profile)
        profile.skills = parsed.skills
        profile.projects = [project.model_dump() for project in parsed.projects]
        profile.experience = [entry.model_dump() for entry in parsed.experience]
        profile.technologies = parsed.technologies
        profile.education = [entry.model_dump() for entry in parsed.education]
        profile.achievements = parsed.achievements
        profile.parser_name = parser_name
        profile.parse_status = ParseStatus.COMPLETED
        profile.parse_error = None
        await self.session.flush()
        await self.session.refresh(profile)
        return profile

    async def upsert_failed(
        self, *, resume_id: UUID, parser_name: str, error_message: str
    ) -> ResumeParsedProfile:
        profile = await self.get_by_resume_id(resume_id)
        if profile is None:
            profile = ResumeParsedProfile(resume_id=resume_id, parser_name=parser_name)
            self.session.add(profile)
        profile.parser_name = parser_name
        profile.parse_status = ParseStatus.FAILED
        profile.parse_error = error_message
        await self.session.flush()
        await self.session.refresh(profile)
        return profile
