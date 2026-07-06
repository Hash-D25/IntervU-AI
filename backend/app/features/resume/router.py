"""Resume upload routes. Thin controller: validate input, delegate to service."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, UploadFile, status

from app.core.container import SettingsDep
from app.features.auth.dependencies import CurrentUserDep
from app.features.resume.dependencies import ResumeServiceDep
from app.features.resume.mapper import to_resume_response
from app.features.resume.schemas import ResumeResponse

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    current_user: CurrentUserDep,
    service: ResumeServiceDep,
    settings: SettingsDep,
    file: Annotated[UploadFile, File()],
) -> ResumeResponse:
    resume = await service.upload(current_user, file)
    return to_resume_response(resume, settings)


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(
    current_user: CurrentUserDep,
    service: ResumeServiceDep,
    settings: SettingsDep,
) -> list[ResumeResponse]:
    resumes = await service.list_for_user(current_user.id)
    return [to_resume_response(resume, settings) for resume in resumes]


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: UUID,
    current_user: CurrentUserDep,
    service: ResumeServiceDep,
    settings: SettingsDep,
) -> ResumeResponse:
    resume = await service.get_for_user(resume_id, current_user.id)
    return to_resume_response(resume, settings)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    current_user: CurrentUserDep,
    service: ResumeServiceDep,
) -> None:
    await service.delete(resume_id, current_user.id)
