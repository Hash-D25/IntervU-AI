"""Select and wire question generation strategies."""

from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.core.exceptions import BadRequestError
from app.features.interview.question_generation.protocols import QuestionGeneratorStrategy
from app.features.interview.question_generation.schemas import QuestionCategory
from app.features.interview.question_generation.strategies.behavioral import (
    BehavioralQuestionStrategy,
)
from app.features.interview.question_generation.strategies.cs_fundamentals import (
    CsFundamentalsQuestionStrategy,
)
from app.features.interview.question_generation.strategies.dsa import DsaQuestionStrategy
from app.features.interview.question_generation.strategies.project import ProjectQuestionStrategy


def create_question_generator_strategies(
    settings: Settings,
) -> dict[QuestionCategory, QuestionGeneratorStrategy]:
    if settings.question_generator != "llm":
        raise BadRequestError(f"Unsupported question generator: {settings.question_generator}")

    llm = create_llm_provider(settings)
    return {
        QuestionCategory.DSA: DsaQuestionStrategy(
            llm,
            model=settings.llm_model,
            disable_thinking=settings.llm_disable_thinking,
        ),
        QuestionCategory.PROJECT: ProjectQuestionStrategy(
            llm,
            model=settings.llm_model,
            disable_thinking=settings.llm_disable_thinking,
        ),
        QuestionCategory.BEHAVIORAL: BehavioralQuestionStrategy(
            llm,
            model=settings.llm_model,
            disable_thinking=settings.llm_disable_thinking,
        ),
        QuestionCategory.CS_FUNDAMENTALS: CsFundamentalsQuestionStrategy(
            llm,
            model=settings.llm_model,
            disable_thinking=settings.llm_disable_thinking,
        ),
    }
