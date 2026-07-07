"""Orchestrate interview question generation."""

from app.features.interview.question_generation.protocols import QuestionGeneratorStrategy
from app.features.interview.question_generation.schemas import (
    QuestionCategory,
    QuestionGenerationContext,
    QuestionGenerationResult,
)
from app.features.interview.question_generation.selector import select_question_categories


class QuestionGenerationService:
    name = "llm"

    def __init__(self, strategies: dict[QuestionCategory, QuestionGeneratorStrategy]) -> None:
        self._strategies = strategies

    async def generate(self, context: QuestionGenerationContext) -> QuestionGenerationResult:
        categories = select_question_categories(context.interview_plan)
        questions = []
        for category in categories:
            strategy = self._strategies[category]
            questions.append(await strategy.generate(context))
        return QuestionGenerationResult(questions=questions, generator_name=self.name)
