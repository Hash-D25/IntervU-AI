"""Build compact prompt context from interview inputs."""

import json

from app.features.interview.question_generation.schemas import QuestionGenerationContext


def build_prompt_context(context: QuestionGenerationContext) -> str:
    payload = {
        "company_name": context.company_name,
        "target_role": context.target_role,
        "interview_type": context.interview_type.value,
        "interview_plan": context.interview_plan.model_dump(mode="json"),
        "resume": {
            "skills": context.resume.skills[:12],
            "technologies": context.resume.technologies[:12],
            "projects": [project.model_dump() for project in context.resume.projects[:4]],
            "experience": [entry.model_dump() for entry in context.resume.experience[:4]],
            "achievements": context.resume.achievements[:6],
        },
        "job_description": (
            context.job_description.model_dump(mode="json") if context.job_description else None
        ),
        "job_description_text": _trim_text(context.job_description_text, 1500),
    }
    return json.dumps(payload, separators=(",", ":"))


def _trim_text(value: str | None, max_chars: int) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars]}...[truncated]"
