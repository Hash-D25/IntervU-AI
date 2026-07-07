"""LLM-based answer evaluation strategy."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.features.evaluation.context_builder import build_evaluation_prompt_context
from app.features.evaluation.json_response import parse_evaluation_response
from app.features.evaluation.schemas import AnswerEvaluationResult, EvaluationContext
from app.features.evaluation.validator import AnswerEvaluationValidator
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt


class LlmAnswerEvaluator:
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
        self._prompt_template = load_prompt("answer_evaluation.txt")

    async def evaluate(self, context: EvaluationContext) -> AnswerEvaluationResult:
        prompt = prepare_llm_prompt(
            self._prompt_template.replace(
                "{context_json}",
                build_evaluation_prompt_context(context),
            ),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        parsed = parse_evaluation_response(raw_response)
        parsed.evaluator_name = self.name
        return AnswerEvaluationValidator.validate(parsed, context=context)


def create_llm_answer_evaluator(settings: Settings) -> LlmAnswerEvaluator:
    return LlmAnswerEvaluator(
        create_llm_provider(settings),
        model=settings.llm_model,
        disable_thinking=settings.llm_disable_thinking,
    )
