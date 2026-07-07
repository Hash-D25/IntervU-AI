"""Post-analysis validation and normalization."""

import re

from app.core.exceptions import ParseError
from app.features.job_description.processing.schemas import ParsedJobDescription
from app.features.job_description.processing.seniority import (
    normalize_seniority_level,
)

_MAX_ITEMS = 50
_MAX_RESPONSIBILITY_LEN = 2000
_BULLET_PREFIX = re.compile(r"^[\s\-*•·∗]+")
_MULTI_SPACE = re.compile(r"\s+")


class ParsedJobDescriptionValidator:
    @classmethod
    def validate(cls, parsed: ParsedJobDescription) -> ParsedJobDescription:
        cls._ensure_list_limits(parsed)
        skills = _normalize_string_list(parsed.skills)
        technologies = _subtract_overlap(skills, _normalize_string_list(parsed.technologies))
        responsibilities = _normalize_responsibilities(parsed.responsibilities)
        seniority = normalize_seniority_level(parsed.seniority_level)
        return ParsedJobDescription(
            skills=skills,
            technologies=technologies,
            responsibilities=responsibilities,
            seniority_level=seniority,
        )

    @classmethod
    def _ensure_list_limits(cls, parsed: ParsedJobDescription) -> None:
        if len(parsed.skills) > _MAX_ITEMS or len(parsed.technologies) > _MAX_ITEMS:
            raise ParseError("Parsed job description contains too many skills or technologies")
        if len(parsed.responsibilities) > _MAX_ITEMS:
            raise ParseError("Parsed job description contains too many responsibilities")


def _normalize_string_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        item = _MULTI_SPACE.sub(" ", _BULLET_PREFIX.sub("", value.strip()))
        if not item:
            continue
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return normalized


def _normalize_responsibilities(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        item = _MULTI_SPACE.sub(" ", _BULLET_PREFIX.sub("", value.strip()))
        if not item or len(item) > _MAX_RESPONSIBILITY_LEN:
            continue
        key = re.sub(r"[^a-z0-9]", "", item.casefold())
        if key in seen:
            continue
        seen.add(key)
        normalized.append(item)
    return normalized


def _subtract_overlap(skills: list[str], technologies: list[str]) -> list[str]:
    skill_keys = {skill.casefold() for skill in skills}
    return [tech for tech in technologies if tech.casefold() not in skill_keys]
