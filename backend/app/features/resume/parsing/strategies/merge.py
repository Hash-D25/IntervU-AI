"""Merge rule-based partial extraction with LLM gap-fill output."""

from collections.abc import Callable

from app.features.resume.parsing.normalization import normalize_string_list
from app.features.resume.parsing.project_names import align_project_names
from app.features.resume.parsing.schemas import (
    EducationEntry,
    ExperienceEntry,
    ParsedResume,
)


def merge_parsed(partial: ParsedResume, llm: ParsedResume) -> ParsedResume:
    projects = (
        align_project_names(partial.projects, llm.projects)
        if partial.projects
        else llm.projects
    )
    return ParsedResume(
        skills=normalize_string_list(partial.skills + llm.skills),
        technologies=normalize_string_list(partial.technologies + llm.technologies),
        projects=projects,
        experience=_merge_experience(partial.experience, llm.experience),
        education=_merge_education(partial.education, llm.education),
        achievements=normalize_string_list(partial.achievements + llm.achievements),
    )


def _merge_experience(
    primary: list[ExperienceEntry], secondary: list[ExperienceEntry]
) -> list[ExperienceEntry]:
    return _merge_entries(
        primary,
        secondary,
        key=lambda entry: f"{entry.title.casefold()}|{(entry.company or '').casefold()}",
    )


def _merge_education(
    primary: list[EducationEntry], secondary: list[EducationEntry]
) -> list[EducationEntry]:
    return _merge_entries(primary, secondary, key=lambda entry: entry.institution.casefold())


def _merge_entries[T](
    primary: list[T], secondary: list[T], *, key: Callable[[T], object]
) -> list[T]:
    seen: set[object] = set()
    merged: list[T] = []
    for entry in primary + secondary:
        entry_key = key(entry)
        if entry_key in seen:
            continue
        seen.add(entry_key)
        merged.append(entry)
    return merged
