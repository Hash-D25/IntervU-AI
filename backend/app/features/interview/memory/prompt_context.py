"""Serialize interview memory for LLM prompts."""

from app.features.interview.memory.schemas import InterviewMemory


def memory_prompt_payload(memory: InterviewMemory | None) -> dict[str, object] | None:
    if memory is None or memory.updated_from_question_count == 0:
        return None
    return {
        "topics_covered": memory.topics_covered,
        "strengths": memory.strengths,
        "weak_areas": memory.weak_areas,
        "notable_mentions": memory.notable_mentions,
        "projects_discussed": memory.projects_discussed,
        "recent_answers": [
            {
                "phase": item.phase,
                "category": item.category,
                "is_follow_up": item.is_follow_up,
                "question_text": item.question_text,
                "answer_excerpt": item.answer_excerpt,
                "key_claims": item.key_claims,
                "overall_score": item.overall_score,
            }
            for item in memory.answers[-4:]
        ],
        "usage_guidance": {
            "callback_style": (
                "When useful, reference prior statements with phrasing like "
                "'You mentioned JWT earlier...' — only using notable_mentions / "
                "key_claims grounded in recent_answers."
            ),
            "avoid": (
                "Do not invent earlier statements. Do not re-ask topics already "
                "covered unless probing a new tradeoff/edge case."
            ),
        },
    }
