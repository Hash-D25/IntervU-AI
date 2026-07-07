"""Prompt helpers for faster, more reliable LLM resume parsing."""

import json

from app.features.resume.parsing.schemas import ParsedResume


def compact_partial_json(partial: ParsedResume) -> str:
    return json.dumps(
        {
            "skills": partial.skills,
            "projects": [project.model_dump() for project in partial.projects],
            "experience": [entry.model_dump() for entry in partial.experience],
                "technologies": partial.technologies,
                "education": [entry.model_dump() for entry in partial.education],
                "achievements": partial.achievements,
            },
        separators=(",", ":"),
    )


def prepare_llm_prompt(prompt: str, *, model: str, disable_thinking: bool) -> str:
    if disable_thinking and "qwen" in model.casefold():
        return f"/no_think\n{prompt}"
    return prompt
