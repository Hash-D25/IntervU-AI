"""CS fundamentals question generation strategy."""

from app.ai.providers.base import LLMProvider
from app.features.interview.question_generation.schemas import QuestionCategory
from app.features.interview.question_generation.strategies.llm_base import LlmQuestionStrategy


class CsFundamentalsQuestionStrategy(LlmQuestionStrategy):
    def __init__(
        self, llm: LLMProvider, *, model: str, disable_thinking: bool
    ) -> None:
        super().__init__(
            llm,
            category=QuestionCategory.CS_FUNDAMENTALS,
            prompt_filename="interview_question_cs_fundamentals.txt",
            model=model,
            disable_thinking=disable_thinking,
        )
