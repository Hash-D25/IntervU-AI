"""LLM-based feedback generation strategy."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.features.feedback.json_response import parse_feedback_response
from app.features.feedback.prompt_context import build_feedback_prompt_context
from app.features.feedback.schemas import FeedbackContext, FeedbackResult
from app.features.feedback.validator import FeedbackValidator
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt


class LlmFeedbackGenerator:
    name = "llm"

    def __init__(
        self,
        llm: LLMProvider,
        *,
        model: str,
        disable_thinking: bool,
    ) -> None:
        self._llm = llm
        self._model = model
        self._disable_thinking = disable_thinking
        self._prompt_template = load_prompt("feedback_generation.txt")

    async def generate(self, context: FeedbackContext) -> FeedbackResult:
        prompt = prepare_llm_prompt(
            self._prompt_template.replace(
                "{context_json}",
                build_feedback_prompt_context(context),
            ),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        parsed = parse_feedback_response(raw_response)
        parsed.generator_name = self.name
        return FeedbackValidator.validate(parsed, context=context)


def create_llm_feedback_generator(settings: Settings) -> LlmFeedbackGenerator:
    return LlmFeedbackGenerator(
        create_llm_provider(settings),
        model=settings.llm_model,
        disable_thinking=settings.llm_disable_thinking,
    )
