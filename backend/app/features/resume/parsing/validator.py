"""Post-parse validation and normalization."""

from app.core.exceptions import ParseError
from app.features.resume.parsing.normalization import (
    normalize_achievements,
    normalize_string_list,
    subtract_overlap,
)
from app.features.resume.parsing.project_names import sanitize_project_name
from app.features.resume.parsing.schemas import ParsedResume, ProjectEntry

_MAX_ITEMS = 50


class ParsedResumeValidator:
    @classmethod
    def validate(cls, parsed: ParsedResume) -> ParsedResume:
        cls._ensure_list_limits(parsed)
        skills = normalize_string_list(parsed.skills)
        project_technologies = _collect_project_technologies(parsed.projects)
        technologies = subtract_overlap(
            skills,
            normalize_string_list(parsed.technologies + project_technologies),
        )
        achievements = normalize_achievements(parsed.achievements)
        projects = _normalize_projects(parsed.projects)
        return ParsedResume(
            skills=skills,
            projects=projects,
            experience=parsed.experience,
            technologies=technologies,
            education=parsed.education,
            achievements=achievements,
        )

    @classmethod
    def _ensure_list_limits(cls, parsed: ParsedResume) -> None:
        if len(parsed.skills) > _MAX_ITEMS or len(parsed.technologies) > _MAX_ITEMS:
            raise ParseError("Parsed resume contains too many items")
        if len(parsed.achievements) > _MAX_ITEMS:
            raise ParseError("Parsed resume contains too many achievements")
        if len(parsed.projects) > _MAX_ITEMS or len(parsed.experience) > _MAX_ITEMS:
            raise ParseError("Parsed resume contains too many entries")
        if len(parsed.education) > _MAX_ITEMS:
            raise ParseError("Parsed resume contains too many education entries")


def _normalize_projects(projects: list[ProjectEntry]) -> list[ProjectEntry]:
    return [
        project.model_copy(update={"name": sanitize_project_name(project.name)})
        for project in projects
    ]


def _collect_project_technologies(projects: list[ProjectEntry]) -> list[str]:
    collected: list[str] = []
    for project in projects:
        collected.extend(project.technologies)
    return collected
