"""LLM follow-up question generation strategy."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.features.interview.follow_up.json_response import parse_follow_up_response
from app.features.interview.follow_up.prompt_context import build_follow_up_prompt_context
from app.features.interview.follow_up.schemas import (
    ExtractedClaim,
    FollowUpContext,
    GeneratedFollowUp,
)
from app.features.interview.follow_up.validator import FollowUpValidator
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt


class LlmFollowUpGenerator:
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
        self._prompt_template = load_prompt("follow_up_generation.txt")

    async def generate(
        self,
        context: FollowUpContext,
        *,
        claims: list[ExtractedClaim],
    ) -> GeneratedFollowUp | None:
        if not claims:
            return None
        prompt = prepare_llm_prompt(
            self._prompt_template.replace(
                "{context_json}",
                build_follow_up_prompt_context(context, claims),
            ),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        parsed = parse_follow_up_response(
            raw_response,
            fallback_category=context.category,
        )
        parsed.generator_name = self.name
        if not parsed.probed_claims:
            parsed.probed_claims = [claim.text for claim in claims[:2]]
        return FollowUpValidator.validate_follow_up(
            parsed,
            previous_follow_ups=context.previous_follow_ups,
            answer_transcript=context.answer_transcript,
            question_text=context.question_text,
        )


def create_llm_follow_up_generator(settings: Settings) -> LlmFollowUpGenerator:
    return LlmFollowUpGenerator(
        create_llm_provider(settings),
        model=settings.llm_model,
        disable_thinking=settings.llm_disable_thinking,
    )
