"""Answer evaluator contract."""

from typing import Protocol

from app.features.evaluation.schemas import AnswerEvaluationResult, EvaluationContext


class AnswerEvaluator(Protocol):
    @property
    def name(self) -> str: ...

    async def evaluate(self, context: EvaluationContext) -> AnswerEvaluationResult: ...
