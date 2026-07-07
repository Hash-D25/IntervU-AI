"""Build compact prompt context for answer evaluation."""

import json

from app.features.evaluation.phase_guidance import (
    extract_answer_signals,
    improvement_guardrails,
    phase_dimension_weights,
    phase_evaluation_instruction,
)
from app.features.evaluation.schemas import EvaluationContext


def build_evaluation_prompt_context(context: EvaluationContext) -> str:
    signals = extract_answer_signals(context.answer_transcript)
    weights = phase_dimension_weights(context.phase)
    payload = {
        "company_name": context.company_name,
        "target_role": context.target_role,
        "question": {
            "text": context.question_text,
            "category": context.category,
            "phase": context.phase,
            "difficulty": context.difficulty,
            "expected_topics": context.expected_topics,
            "evaluation_rubric": context.evaluation_rubric,
        },
        "answer_transcript": context.answer_transcript,
        "evaluation_guidance": {
            "phase_instruction": phase_evaluation_instruction(
                context.phase,
                context.category,
            ),
            "dimension_weights": {dim.value: weight for dim, weight in weights.items()},
            "answer_signals": signals,
            "improvement_guardrails": improvement_guardrails(signals),
        },
    }
    return json.dumps(payload, separators=(",", ":"))
