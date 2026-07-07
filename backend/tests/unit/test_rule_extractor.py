"""Rule-based resume extraction unit tests."""

from app.features.resume.parsing.strategies.rule_extractor import RuleBasedResumeExtractor

SAMPLE_RESUME = """
Jane Doe
Software Engineer

Skills: Python, FastAPI, PostgreSQL, Docker

Experience
Software Engineer — Acme Corp (2022–Present)
Built APIs with FastAPI and PostgreSQL.

Education
B.Tech Computer Science — Example University, 2022
"""


def test_extracts_skills_from_section() -> None:
    partial = RuleBasedResumeExtractor().extract(SAMPLE_RESUME)
    lowered = {skill.casefold() for skill in partial.skills}
    assert "python" in lowered
    assert "fastapi" in lowered
    assert "postgresql" in lowered


def test_scans_keyword_skills_in_body() -> None:
    partial = RuleBasedResumeExtractor().extract(SAMPLE_RESUME)
    lowered = {skill.casefold() for skill in partial.skills}
    assert "docker" in lowered


def test_extracts_achievements_from_section() -> None:
    text = """
Achievements
- Won university hackathon 2023
- Published paper on ML
"""
    partial = RuleBasedResumeExtractor().extract(text)
    assert any("hackathon" in item.casefold() for item in partial.achievements)
