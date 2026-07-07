"""Select an answer evaluation strategy from configuration."""

from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.evaluation.protocols import AnswerEvaluator
from app.features.evaluation.strategies.llm_evaluator import create_llm_answer_evaluator


def create_answer_evaluator(settings: Settings) -> AnswerEvaluator:
    if settings.answer_evaluator == "llm":
        return create_llm_answer_evaluator(settings)
    raise BadRequestError(f"Unsupported answer evaluator: {settings.answer_evaluator}")
