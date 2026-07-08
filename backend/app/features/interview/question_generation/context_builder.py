"""Build compact prompt context from interview inputs."""

import json

from app.features.interview.memory.prompt_context import memory_prompt_payload
from app.features.interview.question_generation.schemas import QuestionGenerationContext
from app.features.resume.parsing.project_names import sanitize_project_name


def build_prompt_context(context: QuestionGenerationContext) -> str:
    projects = context.resume.projects[:4]
    payload = {
        "company_name": context.company_name,
        "target_role": context.target_role,
        "interview_type": context.interview_type.value,
        "interview_plan": context.interview_plan.model_dump(mode="json"),
        "resume": {
            "skills": context.resume.skills[:12],
            "technologies": context.resume.technologies[:12],
            "primary_technologies": _primary_technologies(
                context.resume.skills,
                context.resume.technologies,
            ),
            "canonical_project_names": [
                sanitize_project_name(project.name) for project in projects
            ],
            "projects": [
                project.model_copy(
                    update={"name": sanitize_project_name(project.name)}
                ).model_dump()
                for project in projects
            ],
            "experience": [entry.model_dump() for entry in context.resume.experience[:4]],
            "achievements": context.resume.achievements[:6],
        },
        "job_description": (
            context.job_description.model_dump(mode="json") if context.job_description else None
        ),
        "job_description_text": _trim_text(context.job_description_text, 1500),
        "generation_guidance": {
            "technology_priority": (
                "Prefer questions grounded in resume.primary_technologies and projects "
                "the candidate has actually built. Treat job-description technologies as "
                "secondary unless they also appear on the resume."
            ),
            "project_name_policy": (
                "When referencing projects, copy canonical_project_names exactly. "
                "Use a hyphen (-) not an en/em dash. Never add suffixes like Link or Live."
            ),
        },
    }
    if context.execution_phase is not None:
        payload["execution"] = {
            "phase": context.execution_phase.value,
            "phase_instruction": context.phase_instruction,
            "focus_project_names": context.focus_project_names,
            "comparison_project_names": context.comparison_project_names,
            "projects_already_covered": context.projects_already_covered,
            "previous_question_topics": context.previous_question_topics,
        }
    memory_payload = memory_prompt_payload(context.memory)
    if memory_payload is not None:
        payload["interview_memory"] = memory_payload
    return json.dumps(payload, separators=(",", ":"))


def _primary_technologies(
    skills: list[str], technologies: list[str], *, limit: int = 12
) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for value in [*skills, *technologies]:
        cleaned = value.strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        merged.append(cleaned)
        if len(merged) >= limit:
            break
    return merged


def _trim_text(value: str | None, max_chars: int) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars]}...[truncated]"
