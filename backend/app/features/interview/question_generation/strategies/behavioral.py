"""Behavioral question generation strategy."""

from app.ai.providers.base import LLMProvider
from app.features.interview.question_generation.schemas import QuestionCategory
from app.features.interview.question_generation.strategies.llm_base import LlmQuestionStrategy


class BehavioralQuestionStrategy(LlmQuestionStrategy):
    def __init__(
        self, llm: LLMProvider, *, model: str, disable_thinking: bool
    ) -> None:
        super().__init__(
            llm,
            category=QuestionCategory.BEHAVIORAL,
            prompt_filename="interview_question_behavioral.txt",
            model=model,
            disable_thinking=disable_thinking,
        )
