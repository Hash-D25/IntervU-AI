"""Job description feature dependency wiring."""

from typing import Annotated

from fastapi import Depends

from app.core.container import SettingsDep
from app.features.job_description.processing.factory import create_job_description_analyzer
from app.features.job_description.processing.protocols import JobDescriptionAnalyzer
from app.features.job_description.processing.service import JobDescriptionProcessingService


def get_job_description_analyzer(settings: SettingsDep) -> JobDescriptionAnalyzer:
    return create_job_description_analyzer(settings)


def get_job_description_processing_service(
    analyzer: Annotated[JobDescriptionAnalyzer, Depends(get_job_description_analyzer)],
) -> JobDescriptionProcessingService:
    return JobDescriptionProcessingService(analyzer)


JobDescriptionProcessingServiceDep = Annotated[
    JobDescriptionProcessingService, Depends(get_job_description_processing_service)
]
