"""Resume feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SessionDep, SettingsDep
from app.features.resume.parsed_repository import ResumeParsedProfileRepository
from app.features.resume.parsing.factory import create_resume_parser
from app.features.resume.parsing.protocols import ResumeParser
from app.features.resume.parsing.service import ResumeParsingService
from app.features.resume.repository import ResumeRepository
from app.features.resume.service import ResumeService
from app.features.resume.storage import FileStorageService, create_file_storage_service


def get_resume_repository(session: SessionDep) -> ResumeRepository:
    return ResumeRepository(session)


def get_parsed_profile_repository(session: SessionDep) -> ResumeParsedProfileRepository:
    return ResumeParsedProfileRepository(session)


def get_file_storage_service(settings: SettingsDep) -> FileStorageService:
    return create_file_storage_service(settings)


def get_resume_parser(settings: SettingsDep) -> ResumeParser:
    return create_resume_parser(settings)


def get_resume_service(
    session: SessionDep,
    settings: SettingsDep,
    repository: Annotated[ResumeRepository, Depends(get_resume_repository)],
    storage: Annotated[FileStorageService, Depends(get_file_storage_service)],
) -> ResumeService:
    return ResumeService(session, repository, storage, settings)


def get_resume_parsing_service(
    session: SessionDep,
    resume_repository: Annotated[ResumeRepository, Depends(get_resume_repository)],
    parsed_repository: Annotated[
        ResumeParsedProfileRepository, Depends(get_parsed_profile_repository)
    ],
    storage: Annotated[FileStorageService, Depends(get_file_storage_service)],
    parser: Annotated[ResumeParser, Depends(get_resume_parser)],
) -> ResumeParsingService:
    return ResumeParsingService(session, resume_repository, parsed_repository, storage, parser)


ResumeServiceDep = Annotated[ResumeService, Depends(get_resume_service)]
ResumeParsingServiceDep = Annotated[ResumeParsingService, Depends(get_resume_parsing_service)]
