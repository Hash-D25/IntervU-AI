"""Map internal parsed models to API DTOs."""

from app.features.job_description.processing.schemas import ParsedJobDescription
from app.features.job_description.schemas import JobDescriptionAnalysisResponse


def to_analysis_response(
    parsed: ParsedJobDescription, *, analyzer_name: str
) -> JobDescriptionAnalysisResponse:
    return JobDescriptionAnalysisResponse(
        skills=parsed.skills,
        technologies=parsed.technologies,
        responsibilities=parsed.responsibilities,
        seniority_level=parsed.seniority_level,
        analyzer_name=analyzer_name,
    )
