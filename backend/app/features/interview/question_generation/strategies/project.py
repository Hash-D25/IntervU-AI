"""Project question generation strategy."""

from app.ai.providers.base import LLMProvider
from app.features.interview.question_generation.schemas import QuestionCategory
from app.features.interview.question_generation.strategies.llm_base import LlmQuestionStrategy


class ProjectQuestionStrategy(LlmQuestionStrategy):
    def __init__(
        self, llm: LLMProvider, *, model: str, disable_thinking: bool
    ) -> None:
        super().__init__(
            llm,
            category=QuestionCategory.PROJECT,
            prompt_filename="interview_question_project.txt",
            model=model,
            disable_thinking=disable_thinking,
        )
