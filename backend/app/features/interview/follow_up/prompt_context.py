"""Serialize follow-up context for LLM prompts."""

import json

from app.features.interview.follow_up.schemas import ExtractedClaim, FollowUpContext


def build_claim_prompt_context(context: FollowUpContext) -> str:
    payload = {
        "company_name": context.company_name,
        "target_role": context.target_role,
        "phase": context.phase.value,
        "category": context.category,
        "question_text": context.question_text,
        "answer_transcript": context.answer_transcript,
        "follow_up_strategy": context.follow_up_strategy,
        "focus_areas": context.focus_areas,
        "evaluation": (
            context.evaluation.model_dump(mode="json") if context.evaluation else None
        ),
        "guidance": {
            "extract": (
                "Extract 1-4 concrete claims from the answer that an interviewer "
                "would reasonably probe. Prefer technologies, tradeoffs, ownership, "
                "metrics, and process choices."
            ),
            "avoid": (
                "Do not invent claims absent from the answer. Never treat "
                "question premises, assumptions, or constraints as candidate "
                "claims. Skip fluff and pure motivation statements."
            ),
        },
    }
    return json.dumps(payload, separators=(",", ":"))


def build_follow_up_prompt_context(
    context: FollowUpContext,
    claims: list[ExtractedClaim],
) -> str:
    payload = {
        "company_name": context.company_name,
        "target_role": context.target_role,
        "phase": context.phase.value,
        "category": context.category,
        "question_text": context.question_text,
        "answer_transcript": context.answer_transcript,
        "follow_up_strategy": context.follow_up_strategy,
        "focus_areas": context.focus_areas,
        "previous_follow_ups": context.previous_follow_ups,
        "current_depth": context.current_depth,
        "claims": [claim.model_dump(mode="json") for claim in claims],
        "evaluation": (
            context.evaluation.model_dump(mode="json") if context.evaluation else None
        ),
        "guidance": {
            "style": (
                "Ask one sharp probing follow-up. Example style: "
                "'Why Redis instead of Memcached?' Prefer why/how/tradeoff/"
                "ownership/metrics probes."
            ),
            "constraints": (
                "Do not repeat previous_follow_ups. Stay grounded in claims from "
                "the answer. Never probe a question caveat (e.g. 'assuming no "
                "deletes'). One question only. Keep it concise and interview-natural."
            ),
        },
    }
    return json.dumps(payload, separators=(",", ":"))
