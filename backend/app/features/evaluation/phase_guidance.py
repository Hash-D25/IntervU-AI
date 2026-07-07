"""Phase-aware evaluation guidance and answer signal extraction."""

import re

from app.features.evaluation.schemas import EvaluationDimension

_CP_COUNT = re.compile(
    r"\b\d{2,}\+?\s*(?:problems?|questions?)\b|"
    r"\bsolved\s+\d{2,}\+?\b|"
    r"\b\d{2,}\+?\s+on\s+(?:leetcode|codeforces)\b",
    re.IGNORECASE,
)
_CGPA = re.compile(r"\b(?:cgpa|gpa)\s*[:\s]?\s*\d+(?:\.\d+)?\b", re.IGNORECASE)
_HACKATHON = re.compile(r"\b(?:won|first place|winner|hackathon)\b", re.IGNORECASE)
_COMPANY_MOTIVATION = re.compile(
    r"\b(?:interested in|excited about|drawn to|why)\b.{0,80}\b(?:epam|company|role|internship)\b",
    re.IGNORECASE,
)
_TECH_STACK = re.compile(
    r"\b(?:nestjs|fastapi|postgresql|prisma|jwt|react|python|chrome extension)\b",
    re.IGNORECASE,
)
_PROJECT_NAMES = re.compile(
    r"\b(?:uncdoit|ytnotes|github repository browser|social media app)\b",
    re.IGNORECASE,
)

_PHASE_WEIGHTS: dict[str, dict[EvaluationDimension, float]] = {
    "introduction": {
        EvaluationDimension.TECHNICAL_ACCURACY: 0.6,
        EvaluationDimension.COMPLETENESS: 1.3,
        EvaluationDimension.COMMUNICATION: 1.4,
        EvaluationDimension.DEPTH: 0.7,
        EvaluationDimension.EXAMPLES: 1.2,
    },
    "resume": {
        EvaluationDimension.TECHNICAL_ACCURACY: 1.0,
        EvaluationDimension.COMPLETENESS: 1.1,
        EvaluationDimension.COMMUNICATION: 1.1,
        EvaluationDimension.DEPTH: 1.0,
        EvaluationDimension.EXAMPLES: 1.2,
    },
    "projects": {
        EvaluationDimension.TECHNICAL_ACCURACY: 1.3,
        EvaluationDimension.COMPLETENESS: 1.0,
        EvaluationDimension.COMMUNICATION: 1.0,
        EvaluationDimension.DEPTH: 1.3,
        EvaluationDimension.EXAMPLES: 1.2,
    },
    "cs_fundamentals": {
        EvaluationDimension.TECHNICAL_ACCURACY: 1.4,
        EvaluationDimension.COMPLETENESS: 1.1,
        EvaluationDimension.COMMUNICATION: 1.0,
        EvaluationDimension.DEPTH: 1.2,
        EvaluationDimension.EXAMPLES: 0.9,
    },
    "behavioral": {
        EvaluationDimension.TECHNICAL_ACCURACY: 0.5,
        EvaluationDimension.COMPLETENESS: 1.1,
        EvaluationDimension.COMMUNICATION: 1.3,
        EvaluationDimension.DEPTH: 1.0,
        EvaluationDimension.EXAMPLES: 1.3,
    },
}

_DEFAULT_WEIGHTS: dict[EvaluationDimension, float] = dict.fromkeys(EvaluationDimension, 1.0)

_PHASE_INSTRUCTIONS: dict[str, str] = {
    "introduction": (
        "INTRODUCTION phase: evaluate as a first-impression self-introduction. "
        "Prioritize communication, completeness, motivation, and relevant examples. "
        "Do NOT penalize lightly for lacking deep technical architecture — that is "
        "not expected here. technical_accuracy should reflect whether stated facts "
        "sound plausible, not deep system design."
    ),
    "resume": (
        "RESUME phase: evaluate breadth across experience and projects. "
        "Look for comparisons, connections between internship and projects, "
        "and accurate high-level technical claims."
    ),
    "projects": (
        "PROJECTS phase: evaluate implementation depth, tradeoffs, challenges, "
        "and architecture. technical_accuracy and depth matter most."
    ),
    "cs_fundamentals": (
        "CS_FUNDAMENTALS phase: evaluate conceptual correctness and practical "
        "application. technical_accuracy and depth matter most."
    ),
    "behavioral": (
        "BEHAVIORAL phase: evaluate STAR-style structure, communication, and "
        "specific examples. technical_accuracy is less important unless the "
        "question is technical-behavioral."
    ),
}


def phase_dimension_weights(phase: str) -> dict[EvaluationDimension, float]:
    return dict(_PHASE_WEIGHTS.get(phase, _DEFAULT_WEIGHTS))


def phase_evaluation_instruction(phase: str, category: str) -> str:
    instruction = _PHASE_INSTRUCTIONS.get(
        phase,
        "Score based on how well the answer addresses the specific question asked.",
    )
    if category == "behavioral" and phase != "introduction":
        instruction += " Weight communication and examples heavily."
    return instruction


def extract_answer_signals(transcript: str) -> dict[str, bool]:
    text = transcript.strip()
    return {
        "states_cp_problem_count": bool(_CP_COUNT.search(text)),
        "states_cgpa_or_gpa": bool(_CGPA.search(text)),
        "mentions_hackathon_achievement": bool(_HACKATHON.search(text)),
        "explains_company_or_role_motivation": bool(_COMPANY_MOTIVATION.search(text)),
        "mentions_specific_technologies": bool(_TECH_STACK.search(text)),
        "mentions_named_projects": bool(_PROJECT_NAMES.search(text)),
    }


def improvement_guardrails(signals: dict[str, bool]) -> list[str]:
    guards: list[str] = []
    if signals.get("states_cp_problem_count"):
        guards.append(
            "The answer already quantifies competitive-programming/problem-solving "
            "volume — do NOT suggest adding LeetCode/Codeforces counts."
        )
    if signals.get("states_cgpa_or_gpa"):
        guards.append("The answer already states CGPA/GPA — do NOT suggest adding it.")
    if signals.get("mentions_hackathon_achievement"):
        guards.append(
            "The answer already mentions a hackathon achievement — do NOT suggest "
            "adding hackathon wins."
        )
    if signals.get("explains_company_or_role_motivation"):
        guards.append(
            "The answer already explains motivation for the company/role — suggest "
            "only deeper alignment (values, JD specifics), not 'explain why EPAM'."
        )
    if signals.get("mentions_named_projects"):
        guards.append(
            "The answer already names specific projects — do NOT suggest 'mention "
            "your projects'."
        )
    if signals.get("mentions_specific_technologies"):
        guards.append(
            "The answer already lists specific technologies — suggest deeper usage "
            "or impact, not 'mention tech stack'."
        )
    guards.append(
        "Every improvement MUST address a genuine gap. Never repeat advice for "
        "something already present in answer_transcript."
    )
    return guards
