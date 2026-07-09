"""Job description analysis routes."""

from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from app.core.container import SettingsDep
from app.features.auth.dependencies import CurrentUserDep
from app.features.job_description.dependencies import JobDescriptionProcessingServiceDep
from app.features.job_description.mapper import to_analysis_response
from app.features.job_description.schemas import (
    AnalyzeJobDescriptionRequest,
    JobDescriptionAnalysisResponse,
)
from app.shared.pdf_upload import read_upload_with_size_limit, validate_pdf_content

router = APIRouter(prefix="/job-descriptions", tags=["job-descriptions"])


@router.post(
    "/analyze",
    response_model=JobDescriptionAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_job_description(
    _current_user: CurrentUserDep,
    service: JobDescriptionProcessingServiceDep,
    body: AnalyzeJobDescriptionRequest,
) -> JobDescriptionAnalysisResponse:
    parsed = await service.analyze(body.text)
    return to_analysis_response(parsed, analyzer_name=service.analyzer_name)


@router.post(
    "/analyze/pdf",
    response_model=JobDescriptionAnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_job_description_pdf(
    _current_user: CurrentUserDep,
    service: JobDescriptionProcessingServiceDep,
    settings: SettingsDep,
    file: Annotated[UploadFile, File()],
) -> JobDescriptionAnalysisResponse:
    max_bytes = settings.job_description_max_size_mb * 1024 * 1024
    content = await read_upload_with_size_limit(file, max_bytes)
    validate_pdf_content(content, file.content_type)
    parsed, extracted_text = await service.analyze_pdf_with_text(content)
    return to_analysis_response(
        parsed,
        analyzer_name=service.analyzer_name,
        extracted_text=extracted_text,
    )
