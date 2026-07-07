"""Interview feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SessionDep
from app.features.interview.planning.factory import create_interview_planner
from app.features.interview.planning.protocols import InterviewPlanner
from app.features.interview.repository import InterviewRepository
from app.features.interview.service import InterviewService
from app.features.resume.parsed_repository import ResumeParsedProfileRepository
from app.features.resume.repository import ResumeRepository


def get_interview_repository(session: SessionDep) -> InterviewRepository:
    return InterviewRepository(session)


def get_resume_repository(session: SessionDep) -> ResumeRepository:
    return ResumeRepository(session)


def get_parsed_resume_repository(session: SessionDep) -> ResumeParsedProfileRepository:
    return ResumeParsedProfileRepository(session)


def get_interview_planner() -> InterviewPlanner:
    return create_interview_planner()


def get_interview_service(
    session: SessionDep,
    interviews: Annotated[InterviewRepository, Depends(get_interview_repository)],
    resumes: Annotated[ResumeRepository, Depends(get_resume_repository)],
    parsed_resumes: Annotated[ResumeParsedProfileRepository, Depends(get_parsed_resume_repository)],
    planner: Annotated[InterviewPlanner, Depends(get_interview_planner)],
) -> InterviewService:
    return InterviewService(session, interviews, resumes, parsed_resumes, planner)


InterviewServiceDep = Annotated[InterviewService, Depends(get_interview_service)]
