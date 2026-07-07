"""Serialize feedback context for LLM prompts."""

import json

from app.features.evaluation.phase_guidance import extract_answer_signals, improvement_guardrails
from app.features.feedback.context_builder import strongest_dimensions, weakest_dimensions
from app.features.feedback.schemas import FeedbackContext


def build_feedback_prompt_context(context: FeedbackContext) -> str:
    transcripts = [item.answer_transcript for item in context.evaluated_answers]
    combined_transcript = "\n".join(transcripts)
    interview_signals = extract_answer_signals(combined_transcript)
    guardrails = improvement_guardrails(interview_signals)
    guardrails.extend(_interview_synthesis_guardrails(interview_signals, context))

    payload = {
        "company_name": context.company_name,
        "target_role": context.target_role,
        "interview_type": context.interview_type,
        "overall_average_score": context.overall_average_score,
        "dimension_averages": context.dimension_averages,
        "strongest_dimensions": strongest_dimensions(context.dimension_averages),
        "weakest_dimensions": weakest_dimensions(context.dimension_averages),
        "recurring_strengths": context.recurring_strengths,
        "recurring_improvements": context.recurring_improvements,
        "interview_signals": interview_signals,
        "evaluated_answers": [
            {
                "position": item.position,
                "phase": item.phase,
                "category": item.category,
                "question_text": item.question_text,
                "answer_transcript": _trim_text(item.answer_transcript, 1200),
                "overall_score": item.overall_score,
                "dimension_scores": [
                    score.model_dump(mode="json") for score in item.dimension_scores
                ],
                "answer_strengths": item.answer_strengths,
                "answer_improvements": item.answer_improvements,
            }
            for item in context.evaluated_answers
        ],
        "generation_guidance": {
            "tone": (
                "Coach, not judge. Be constructive, specific, and actionable. "
                "Prefer 'areas to strengthen' over harsh criticism."
            ),
            "synthesis": (
                "SYNTHESIZE patterns across the whole interview. Do NOT copy "
                "answer_improvements or recurring_improvements verbatim into "
                "weaknesses or recommendations. Frame weaknesses as observations "
                "(e.g. 'Depth varied across phases') not imperatives ('Offer more...')."
            ),
            "recommendations": (
                "Give practical next steps the candidate can apply before their next "
                "interview. Each item must address a genuine gap not already covered "
                "in any answer_transcript."
            ),
            "learning_roadmap": (
                "Provide a sequenced study/practice plan for the next 2-4 weeks."
            ),
            "synthesis_guardrails": guardrails,
        },
    }
    return json.dumps(payload, separators=(",", ":"))


def _interview_synthesis_guardrails(
    signals: dict[str, bool],
    context: FeedbackContext,
) -> list[str]:
    guards: list[str] = [
        "Weaknesses and recommendations must be interview-level synthesis, "
        "not a bullet list of per-answer improvements.",
    ]
    if signals.get("states_cp_problem_count"):
        guards.append(
            "Do NOT suggest adding competitive-programming volume or DSA context — "
            "the candidate already quantified problem-solving practice."
        )
    if signals.get("explains_company_or_role_motivation") and signals.get("mentions_named_projects"):
        guards.append(
            "Do NOT suggest 'explain why EPAM' or 'align projects with EPAM' generically — "
            "motivation and projects were already stated. Suggest deeper alignment only "
            "(specific EPAM values, tech stack, or role expectations)."
        )
    weak = weakest_dimensions(context.dimension_averages, limit=1)
    if weak:
        guards.append(
            f"Primary growth area from dimension averages: {weak[0]}. "
            "Center weaknesses and roadmap on that dimension with evidence."
        )
    return guards


def _trim_text(value: str, max_chars: int) -> str:
    cleaned = value.strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars]}...[truncated]"
