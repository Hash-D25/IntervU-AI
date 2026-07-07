"""Parsed resume validation unit tests."""

from app.features.resume.parsing.schemas import ParsedResume
from app.features.resume.parsing.validator import ParsedResumeValidator


def test_validator_deduplicates_skills_case_insensitively() -> None:
    parsed = ParsedResume(
        skills=["Python", "python", " FastAPI "],
        technologies=["Python", "postgres", "postgresql"],
    )
    validated = ParsedResumeValidator.validate(parsed)

    assert validated.skills == ["Python", "FastAPI"]
    assert validated.technologies == ["postgres"]
