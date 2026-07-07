"""Question generator strategy contract."""

from typing import Protocol

from app.features.interview.question_generation.schemas import (
    GeneratedQuestion,
    QuestionCategory,
    QuestionGenerationContext,
)


class QuestionGeneratorStrategy(Protocol):
    @property
    def category(self) -> QuestionCategory: ...

    async def generate(self, context: QuestionGenerationContext) -> GeneratedQuestion: ...
