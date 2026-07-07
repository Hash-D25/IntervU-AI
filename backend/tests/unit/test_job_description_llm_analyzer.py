"""LLM job description analyzer unit tests."""

import json

from app.ai.providers.base import ChatMessage
from app.features.job_description.processing.seniority import SeniorityLevel
from app.features.job_description.processing.strategies.llm_analyzer import (
    LlmJobDescriptionAnalyzer,
)

SAMPLE_JD = """
Senior Software Engineer

We are looking for a senior backend engineer to build scalable APIs.

Requirements:
- 5+ years of Python experience
- Strong PostgreSQL and FastAPI skills
- Experience with AWS and Docker

Responsibilities:
- Design and implement REST APIs
- Mentor junior engineers
"""


class _FakeLLM:
    async def generate(self, messages: list[ChatMessage]) -> str:
        assert "Senior Software Engineer" in messages[0].content
        return json.dumps(
            {
                "skills": ["Python", "System Design", "Mentoring"],
                "technologies": ["PostgreSQL", "FastAPI", "AWS", "Docker", "Python"],
                "responsibilities": [
                    "Design and implement REST APIs",
                    "Mentor junior engineers",
                ],
                "seniority_level": "senior",
            }
        )


async def test_llm_analyzer_extracts_structured_output() -> None:
    analyzer = LlmJobDescriptionAnalyzer(
        _FakeLLM(),  # type: ignore[arg-type]
        model="llama-3.1-8b-instant",
        max_jd_chars=8000,
        disable_thinking=False,
    )
    parsed = await analyzer.analyze(SAMPLE_JD)

    assert "Python" in parsed.skills
    assert "FastAPI" in parsed.technologies
    assert "Python" not in parsed.technologies
    assert parsed.seniority_level == SeniorityLevel.SENIOR
    assert len(parsed.responsibilities) == 2
