"""Resume text trimming unit tests."""

from app.features.resume.parsing.text_trim import trim_resume_for_llm

SAMPLE = """
Jane Doe
Summary
Experienced engineer.

Skills: Python

Experience
Software Engineer — Acme Corp
Built APIs.

Education
B.Tech — Example University, 2022

Certifications
AWS Certified
"""


def test_trim_keeps_relevant_sections_only() -> None:
    trimmed = trim_resume_for_llm(SAMPLE, max_chars=6000)
    assert "Software Engineer" in trimmed
    assert "Example University" in trimmed
    assert "Certifications" not in trimmed


def test_trim_truncates_long_text() -> None:
    long_text = "Experience\n" + ("line\n" * 5000)
    trimmed = trim_resume_for_llm(long_text, max_chars=500)
    assert len(trimmed) <= 520
    assert trimmed.endswith("...[truncated]")
