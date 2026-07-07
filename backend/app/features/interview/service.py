"""Interview session orchestration."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestError, NotFoundError
from app.features.interview.models import Interview, InterviewStatus
from app.features.interview.planning.protocols import InterviewPlanner
from app.features.interview.planning.schemas import InterviewType
from app.features.interview.repository import InterviewRepository
from app.features.resume.parsed_models import ParseStatus
from app.features.resume.parsed_repository import ResumeParsedProfileRepository
from app.features.resume.parsing.schemas import ParsedResume
from app.features.resume.repository import ResumeRepository


class InterviewService:
    def __init__(
        self,
        session: AsyncSession,
        interviews: InterviewRepository,
        resumes: ResumeRepository,
        parsed_resumes: ResumeParsedProfileRepository,
        planner: InterviewPlanner,
    ) -> None:
        self._session = session
        self._interviews = interviews
        self._resumes = resumes
        self._parsed_resumes = parsed_resumes
        self._planner = planner

    async def create(
        self,
        *,
        user_id: UUID,
        resume_id: UUID,
        company_name: str,
        target_role: str,
        interview_type: InterviewType,
        job_description: str | None = None,
    ) -> Interview:
        resume = await self._resumes.get_for_user(resume_id, user_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        parsed_profile = await self._parsed_resumes.get_by_resume_id(resume_id)
        if parsed_profile is None or parsed_profile.parse_status != ParseStatus.COMPLETED:
            raise BadRequestError("Resume must be parsed before creating an interview")

        parsed_resume = ParsedResume(
            skills=parsed_profile.skills,
            projects=parsed_profile.projects,
            experience=parsed_profile.experience,
            technologies=parsed_profile.technologies,
            education=parsed_profile.education,
            achievements=parsed_profile.achievements,
        )
        normalized_job_description = _normalize_job_description(job_description)
        blueprint = await self._planner.build_plan(
            parsed_resume,
            company_name=company_name.strip(),
            target_role=target_role.strip(),
            interview_type=interview_type,
            job_description=normalized_job_description,
        )
        interview = Interview(
            user_id=user_id,
            resume_id=resume_id,
            role=target_role.strip(),
            company=company_name.strip(),
            job_description=normalized_job_description,
            interview_type=interview_type,
            status=InterviewStatus.CREATED,
            session_state=blueprint.session_state.current,
            interview_metadata=blueprint.metadata.model_dump(mode="json"),
            interview_plan=blueprint.interview_plan.model_dump(mode="json"),
        )
        created = await self._interviews.add(interview)
        await self._session.commit()
        return created

    async def get_for_user(self, interview_id: UUID, user_id: UUID) -> Interview:
        interview = await self._interviews.get_for_user(interview_id, user_id)
        if interview is None:
            raise NotFoundError("Interview not found")
        return interview


def _normalize_job_description(job_description: str | None) -> str | None:
    if job_description is None:
        return None
    cleaned = job_description.strip()
    return cleaned or None
