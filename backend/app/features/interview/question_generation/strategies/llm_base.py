"""Shared LLM question generation logic."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.features.interview.question_generation.context_builder import build_prompt_context
from app.features.interview.question_generation.difficulty import infer_difficulty
from app.features.interview.question_generation.json_response import parse_question_response
from app.features.interview.question_generation.schemas import (
    GeneratedQuestion,
    QuestionCategory,
    QuestionGenerationContext,
)
from app.features.interview.question_generation.validator import GeneratedQuestionValidator
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt


class LlmQuestionStrategy:
    def __init__(
        self,
        llm: LLMProvider,
        *,
        category: QuestionCategory,
        prompt_filename: str,
        model: str,
        disable_thinking: bool,
    ) -> None:
        self._llm = llm
        self._category = category
        self._prompt_template = load_prompt(prompt_filename)
        self._model = model
        self._disable_thinking = disable_thinking

    @property
    def category(self) -> QuestionCategory:
        return self._category

    async def generate(self, context: QuestionGenerationContext) -> GeneratedQuestion:
        seniority = context.job_description.seniority_level if context.job_description else None
        difficulty = infer_difficulty(seniority)
        prompt = prepare_llm_prompt(
            self._prompt_template.replace("{difficulty}", difficulty.value).replace(
                "{context_json}", build_prompt_context(context)
            ),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        parsed = parse_question_response(raw_response, self._category)
        return GeneratedQuestionValidator.validate(parsed)
