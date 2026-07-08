"""Deterministic memory rebuild from SessionContext (no LLM / no I/O)."""

import re

from app.features.interview.execution.schemas import SessionContext, SessionQuestion
from app.features.interview.memory.schemas import InterviewMemory, MemoryAnswerSnippet

_TECH_TERMS = re.compile(
    r"\b(?:jwt|oauth|redis|memcached|fastapi|postgresql|postgres|prisma|"
    r"nestjs|docker|kubernetes|react|typescript|python|chrome extension|"
    r"websocket|graphql|mongodb|sqlite|celery|rabbitmq|kafka|nginx|"
    r"aws|gcp|azure|leetcode|codeforces|rest(?:ful)?(?:\s+api)?s?|"
    r"sql|orm|cicd|ci/cd)\b",
    re.IGNORECASE,
)
_MULTI_SPACE = re.compile(r"\s+")


class SessionMemoryBuilder:
    """Rebuild interview memory from answered questions in session context."""

    name = "session"

    def __init__(
        self,
        *,
        max_answers: int = 8,
        excerpt_chars: int = 280,
    ) -> None:
        self._max_answers = max_answers
        self._excerpt_chars = excerpt_chars

    def rebuild(self, session: SessionContext) -> InterviewMemory:
        snippets: list[MemoryAnswerSnippet] = []
        for question in session.questions:
            snippet = _snippet_from_question(
                question,
                excerpt_chars=self._excerpt_chars,
            )
            if snippet is not None:
                snippets.append(snippet)

        truncated = snippets[-self._max_answers :]
        return InterviewMemory(
            answers=truncated,
            topics_covered=_dedupe(
                [topic for item in snippets for topic in item.mentioned_topics]
            ),
            strengths=_dedupe([item for snippet in snippets for item in snippet.strengths]),
            weak_areas=_dedupe([item for snippet in snippets for item in snippet.weak_areas]),
            notable_mentions=_dedupe(
                [item for snippet in snippets for item in snippet.key_claims]
            ),
            projects_discussed=_infer_projects(snippets),
            dimension_averages=_dimension_averages(session),
            updated_from_question_count=len(snippets),
        )


class NoOpMemoryBuilder:
    name = "none"

    def rebuild(self, session: SessionContext) -> InterviewMemory:
        return InterviewMemory()


def _snippet_from_question(
    question: SessionQuestion,
    *,
    excerpt_chars: int,
) -> MemoryAnswerSnippet | None:
    if not question.answered or not question.answer_transcript:
        return None
    transcript = question.answer_transcript.strip()
    if not transcript:
        return None

    evaluation = question.evaluation
    topics = _dedupe([*question.expected_topics, *question.probed_claims])
    tech_mentions = _extract_tech_mentions(transcript)
    key_claims = _dedupe([*question.probed_claims, *tech_mentions])[:6]

    return MemoryAnswerSnippet(
        question_id=question.id,
        position=question.position,
        phase=question.phase.value,
        category=question.category,
        is_follow_up=question.is_follow_up,
        question_text=_trim(question.text, 120),
        answer_excerpt=_trim(transcript, excerpt_chars),
        mentioned_topics=_dedupe([*topics, *tech_mentions])[:8],
        overall_score=evaluation.overall_score if evaluation else None,
        strengths=(evaluation.strengths[:3] if evaluation else []),
        weak_areas=(evaluation.improvements[:3] if evaluation else []),
        key_claims=key_claims,
    )


def _extract_tech_mentions(transcript: str) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for match in _TECH_TERMS.finditer(transcript):
        token = match.group(0).strip()
        key = token.casefold()
        if key in seen:
            continue
        seen.add(key)
        found.append(token)
    return found


def _infer_projects(snippets: list[MemoryAnswerSnippet]) -> list[str]:
    """Best-effort project recall from project-phase topics (no LLM)."""
    found: list[str] = []
    for snippet in snippets:
        if snippet.phase not in {"projects", "resume"}:
            continue
        found.extend(snippet.mentioned_topics)
    return _dedupe(found, limit=6)


def _dimension_averages(session: SessionContext) -> dict[str, float]:
    totals: dict[str, list[float]] = {}
    overalls: list[float] = []
    for question in session.questions:
        evaluation = question.evaluation
        if evaluation is None:
            continue
        overalls.append(evaluation.overall_score)
        for score in evaluation.scores:
            totals.setdefault(score.dimension.value, []).append(score.score)
    averages = {
        name: round(sum(values) / len(values), 2)
        for name, values in totals.items()
        if values
    }
    if overalls:
        averages["overall"] = round(sum(overalls) / len(overalls), 2)
    return averages


def _dedupe(values: list[str], *, limit: int = 8) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        cleaned = _MULTI_SPACE.sub(" ", value.strip())
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
        if len(ordered) >= limit:
            break
    return ordered


def _trim(value: str, max_chars: int) -> str:
    cleaned = _MULTI_SPACE.sub(" ", value.strip())
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[: max_chars - 3]}..."
