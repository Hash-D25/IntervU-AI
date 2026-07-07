"""Post-LLM refinement: remove contradictions and verbatim per-answer recycling."""

from app.features.evaluation.improvement_filter import filter_contradictory_improvements
from app.features.feedback.context_builder import weakest_dimensions
from app.features.feedback.schemas import FeedbackContext, FeedbackResult

_MIN_WEAKNESSES = 2
_MIN_RECOMMENDATIONS = 3


def refine_feedback(feedback: FeedbackResult, context: FeedbackContext) -> FeedbackResult:
    transcripts = [answer.answer_transcript for answer in context.evaluated_answers]
    combined = "\n".join(transcripts)
    per_answer_improvements = [
        item for answer in context.evaluated_answers for item in answer.answer_improvements
    ]

    weaknesses = _filter_section(
        feedback.weaknesses,
        combined,
        per_answer_improvements,
    )
    recommendations = _filter_section(
        feedback.recommendations,
        combined,
        per_answer_improvements,
    )
    learning_roadmap = _filter_section(
        feedback.learning_roadmap,
        combined,
        per_answer_improvements,
        allow_recycle=True,
    )

    weaknesses = _ensure_minimum(
        weaknesses,
        _synthesized_weaknesses(context),
        minimum=_MIN_WEAKNESSES,
    )
    recommendations = _ensure_minimum(
        recommendations,
        _synthesized_recommendations(context),
        minimum=_MIN_RECOMMENDATIONS,
    )

    return FeedbackResult(
        summary=feedback.summary,
        strengths=feedback.strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        learning_roadmap=learning_roadmap or feedback.learning_roadmap,
        overall_score=feedback.overall_score,
        generator_name=feedback.generator_name,
    )


def _filter_section(
    items: list[str],
    combined_transcript: str,
    per_answer_improvements: list[str],
    *,
    allow_recycle: bool = False,
) -> list[str]:
    filtered = filter_contradictory_improvements(items, combined_transcript)
    if allow_recycle:
        return filtered
    return [item for item in filtered if not _is_verbatim_recycle(item, per_answer_improvements)]


def _is_verbatim_recycle(item: str, per_answer_improvements: list[str]) -> bool:
    normalized = _normalize_phrase(item)
    if not normalized:
        return False
    for improvement in per_answer_improvements:
        candidate = _normalize_phrase(improvement)
        if not candidate:
            continue
        if normalized == candidate:
            return True
        if len(normalized) >= 40 and (normalized in candidate or candidate in normalized):
            return True
    return False


def _normalize_phrase(value: str) -> str:
    return " ".join(value.casefold().split())


def _ensure_minimum(items: list[str], fallbacks: list[str], *, minimum: int) -> list[str]:
    result = list(items)
    seen = {_normalize_phrase(item) for item in result}
    for fallback in fallbacks:
        if len(result) >= minimum:
            break
        key = _normalize_phrase(fallback)
        if key in seen:
            continue
        seen.add(key)
        result.append(fallback)
    return result


def _synthesized_weaknesses(context: FeedbackContext) -> list[str]:
    weak_dims = weakest_dimensions(context.dimension_averages, limit=2)
    fallbacks: list[str] = []

    if "depth" in weak_dims:
        fallbacks.append(
            "Technical depth varied across phases — project and intro stories would "
            "be stronger with one concrete decision, tradeoff, or metric each."
        )
    if "examples" in weak_dims:
        fallbacks.append(
            "Some answers could use sharper evidence (latency numbers, scale, or "
            "before/after outcomes) to make impact more tangible."
        )
    if not fallbacks:
        fallbacks.append(
            "Focus on deepening the 'why' behind design choices, not just listing "
            "what was built."
        )
    return fallbacks


def _synthesized_recommendations(context: FeedbackContext) -> list[str]:
    company = context.company_name
    role = context.target_role
    weak_dims = weakest_dimensions(context.dimension_averages, limit=1)
    primary_gap = weak_dims[0] if weak_dims else "depth"

    mapping = {
        "depth": (
            "Practice one 90-second 'deep dive' per project: problem → approach → "
            "tradeoff → outcome."
        ),
        "examples": (
            "Add one quantified outcome to each project story (users, latency, "
            "error rate, or time saved)."
        ),
        "technical_accuracy": (
            "Revisit fundamentals for your stack and rehearse explaining correctness "
            "and edge cases out loud."
        ),
        "completeness": (
            "Use a checklist per answer: context, action, result, and lesson learned."
        ),
        "communication": (
            "Record mock answers and tighten pacing — aim for clear signposting "
            "in the first 20 seconds."
        ),
    }
    return [
        mapping.get(primary_gap, mapping["depth"]),
        f"Run a timed mock {role} interview targeting {company}'s typical stack "
        "and project-deep-dive questions.",
        "After each practice answer, write one tradeoff you would mention if asked "
        "'why not X instead?'",
    ]
