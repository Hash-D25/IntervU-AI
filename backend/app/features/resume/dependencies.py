"""Resume feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SessionDep, SettingsDep
from app.features.resume.repository import ResumeRepository
from app.features.resume.service import ResumeService
from app.features.resume.storage import FileStorageService, create_file_storage_service


def get_resume_repository(session: SessionDep) -> ResumeRepository:
    return ResumeRepository(session)


def get_file_storage_service(settings: SettingsDep) -> FileStorageService:
    return create_file_storage_service(settings)


def get_resume_service(
    session: SessionDep,
    settings: SettingsDep,
    repository: Annotated[ResumeRepository, Depends(get_resume_repository)],
    storage: Annotated[FileStorageService, Depends(get_file_storage_service)],
) -> ResumeService:
    return ResumeService(session, repository, storage, settings)


ResumeServiceDep = Annotated[ResumeService, Depends(get_resume_service)]
