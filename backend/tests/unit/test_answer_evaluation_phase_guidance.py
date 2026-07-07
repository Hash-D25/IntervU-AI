"""Phase-aware evaluation guidance tests."""

from app.features.evaluation.phase_guidance import (
    extract_answer_signals,
    improvement_guardrails,
    phase_dimension_weights,
)
from app.features.evaluation.schemas import EvaluationDimension


def test_introduction_phase_weights_communication_higher() -> None:
    weights = phase_dimension_weights("introduction")

    assert (
        weights[EvaluationDimension.COMMUNICATION]
        > weights[EvaluationDimension.TECHNICAL_ACCURACY]
    )
    assert weights[EvaluationDimension.COMPLETENESS] > weights[EvaluationDimension.DEPTH]


def test_extract_answer_signals_detects_cp_count() -> None:
    signals = extract_answer_signals(
        "I solved 800+ problems on LeetCode and Codeforces."
    )

    assert signals["states_cp_problem_count"] is True


def test_improvement_guardrails_for_quantified_cp() -> None:
    signals = extract_answer_signals("Solved 800+ problems on LeetCode.")
    guards = improvement_guardrails(signals)

    assert any("do not suggest" in guard.lower() for guard in guards)
    assert any("leetcode" in guard.lower() for guard in guards)
