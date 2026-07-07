"""Trim resume text before sending to an LLM — fewer tokens, faster inference."""

import re

_RELEVANT_SECTIONS = frozenset(
    {
        "experience",
        "work experience",
        "employment",
        "professional experience",
        "employment history",
        "education",
        "academic",
        "qualifications",
        "projects",
        "personal projects",
        "project experience",
        "achievements",
        "awards",
        "honors",
        "accomplishments",
        "key achievements",
    }
)

_SECTION_HEADER = re.compile(
    r"^(?:experience|work experience|employment|professional experience|"
    r"employment history|education|academic(?:\s+background)?|qualifications|"
    r"projects|personal projects|project experience|skills|technical skills|"
    r"achievements|awards|honors|accomplishments|key achievements|"
    r"summary|objective|certifications)\s*:?\s*$",
    re.IGNORECASE,
)


def trim_resume_for_llm(text: str, max_chars: int) -> str:
    return _extract_relevant_sections(text, max_chars)


def _extract_relevant_sections(text: str, max_chars: int) -> str:
    lines = text.splitlines()
    captured: list[str] = []
    include = False

    for line in lines:
        stripped = line.strip()
        if stripped and _SECTION_HEADER.match(stripped):
            include = _normalize_header(stripped) in _RELEVANT_SECTIONS
        if include:
            captured.append(line)

    excerpt = "\n".join(captured).strip()
    if captured:
        if len(excerpt) <= max_chars:
            return excerpt
        return f"{excerpt[:max_chars]}\n...[truncated]"
    if len(text) <= max_chars:
        return text.strip()
    return f"{text.strip()[:max_chars]}\n...[truncated]"


def _normalize_header(header: str) -> str:
    return header.casefold().rstrip(":").strip()
