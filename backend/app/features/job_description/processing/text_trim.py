"""Trim job description text before sending to an LLM."""


def trim_job_description_for_llm(text: str, max_chars: int) -> str:
    cleaned = text.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars]}\n...[truncated]"
