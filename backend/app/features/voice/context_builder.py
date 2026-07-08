"""Build Whisper prompts and hint terms from interview context."""

from app.features.interview.planning.schemas import InterviewMetadata
from app.features.voice.schemas import TranscriptionContext

_MAX_PROMPT_CHARS = 800
_MAX_HINT_TERMS = 48


def build_transcription_context(metadata: InterviewMetadata) -> TranscriptionContext:
    hint_terms = _collect_hint_terms(metadata)
    initial_prompt = _build_initial_prompt(metadata, hint_terms)
    return TranscriptionContext(
        initial_prompt=initial_prompt,
        hint_terms=hint_terms,
        company_name=metadata.company_name,
        target_role=metadata.target_role,
    )


def empty_transcription_context() -> TranscriptionContext:
    return TranscriptionContext()


def _collect_hint_terms(metadata: InterviewMetadata) -> list[str]:
    summary = metadata.resume_summary
    raw_terms = [
        metadata.company_name,
        metadata.target_role,
        *summary.skills,
        *summary.technologies,
        *summary.project_names,
        *summary.experience_titles,
        "B.Tech",
        "REST APIs",
        "authentication",
        "competitive programming",
        "LeetCode",
        "Codeforces",
        "PostgreSQL",
        "FastAPI",
        "React",
        "Chrome extension",
        "YouTube",
    ]
    return _dedupe_terms(raw_terms)


def _build_initial_prompt(metadata: InterviewMetadata, hint_terms: list[str]) -> str:
    lead = (
        f"Technical interview answer for {metadata.target_role} at {metadata.company_name}. "
        "Mentioned terms may include: "
    )
    body = ", ".join(hint_terms[:_MAX_HINT_TERMS])
    prompt = f"{lead}{body}."
    if len(prompt) <= _MAX_PROMPT_CHARS:
        return prompt
    return prompt[: _MAX_PROMPT_CHARS - 3] + "..."


def _dedupe_terms(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        cleaned = " ".join(value.strip().split())
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
    return ordered
