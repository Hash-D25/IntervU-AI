"""Hybrid resume parser unit tests."""

import json

import pytest

from app.ai.providers.base import ChatMessage
from app.features.resume.parsing.schemas import (
    EducationEntry,
    ExperienceEntry,
    ParsedResume,
    ProjectEntry,
)
from app.features.resume.parsing.strategies.hybrid_parser import HybridResumeParser
from app.features.resume.parsing.strategies.rule_extractor import RuleBasedResumeExtractor

SAMPLE_RESUME = """
Jane Doe
Skills: Python, FastAPI, PostgreSQL
"""


class _FakeLLM:
    async def generate(self, messages: list[ChatMessage]) -> str:
        prompt = messages[0].content
        assert "partial" in prompt.casefold() or "extract structured" in prompt.casefold()
        return json.dumps(
            {
                "skills": ["Python"],
                "projects": [ProjectEntry(name="InterviewerAI").model_dump()],
                "experience": [ExperienceEntry(title="Engineer", company="Acme").model_dump()],
                "technologies": ["PostgreSQL"],
                "education": [
                    EducationEntry(institution="Example University", degree="B.Tech").model_dump()
                ],
                "achievements": ["Dean's List 2022"],
            }
        )


class _CompletePartialExtractor(RuleBasedResumeExtractor):
    def extract(self, text: str) -> ParsedResume:
        return ParsedResume(
            skills=["Python"],
            technologies=["PostgreSQL"],
            projects=[ProjectEntry(name="Side Project")],
            experience=[ExperienceEntry(title="Engineer", company="Acme")],
            education=[EducationEntry(institution="Example University")],
            achievements=["Hackathon winner"],
        )


async def test_hybrid_parser_merges_rule_extraction_with_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.features.resume.parsing.strategies.hybrid_parser.extract_text_from_pdf",
        lambda _pdf_bytes: SAMPLE_RESUME,
    )
    parser = HybridResumeParser(
        _FakeLLM(),  # type: ignore[arg-type]
        model="qwen3:8b",
        max_resume_chars=6000,
        disable_thinking=False,
    )
    parsed = await parser.parse(b"%PDF-1.4")

    assert "Python" in parsed.skills
    assert parsed.projects[0].name == "InterviewerAI"
    assert parsed.experience[0].company == "Acme"
    assert any("postgres" in skill.casefold() for skill in parsed.skills)


async def test_hybrid_parser_skips_llm_when_partial_is_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.features.resume.parsing.strategies.hybrid_parser.extract_text_from_pdf",
        lambda _pdf_bytes: SAMPLE_RESUME,
    )
    class _ShouldNotRunLLM:
        async def generate(self, messages: list[ChatMessage]) -> str:
            pytest.fail("LLM should not be called when partial extraction is complete")

    parser = HybridResumeParser(
        _ShouldNotRunLLM(),  # type: ignore[arg-type]
        extractor=_CompletePartialExtractor(),
        model="qwen3:8b",
        max_resume_chars=6000,
        disable_thinking=False,
    )
    parsed = await parser.parse(b"%PDF-1.4")

    assert parsed.projects[0].name == "Side Project"
    assert parsed.experience[0].title == "Engineer"
