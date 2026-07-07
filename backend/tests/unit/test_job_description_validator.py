"""Job description validator unit tests."""

from app.features.job_description.processing.schemas import ParsedJobDescription
from app.features.job_description.processing.seniority import SeniorityLevel
from app.features.job_description.processing.validator import ParsedJobDescriptionValidator


def test_validator_deduplicates_skills_and_technologies() -> None:
    parsed = ParsedJobDescription(
        skills=["Python", "python", "Communication"],
        technologies=["Python", "FastAPI", "PostgreSQL"],
        responsibilities=["Build APIs", "Build APIs"],
        seniority_level=SeniorityLevel.SENIOR,
    )
    validated = ParsedJobDescriptionValidator.validate(parsed)
    assert validated.skills == ["Python", "Communication"]
    assert validated.technologies == ["FastAPI", "PostgreSQL"]
    assert validated.responsibilities == ["Build APIs"]
    assert validated.seniority_level == SeniorityLevel.SENIOR


def test_validator_normalizes_seniority_aliases() -> None:
    parsed = ParsedJobDescription(
        skills=[],
        technologies=[],
        responsibilities=[],
        seniority_level="Mid-level",
    )
    validated = ParsedJobDescriptionValidator.validate(parsed)
    assert validated.seniority_level == SeniorityLevel.MID
