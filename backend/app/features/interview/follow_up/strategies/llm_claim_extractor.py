"""LLM claim extraction strategy."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.features.interview.follow_up.json_response import parse_claims_response
from app.features.interview.follow_up.prompt_context import build_claim_prompt_context
from app.features.interview.follow_up.schemas import ExtractedClaim, FollowUpContext
from app.features.interview.follow_up.validator import FollowUpValidator
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt


class LlmClaimExtractor:
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
        self._prompt_template = load_prompt("claim_extraction.txt")

    async def extract(self, context: FollowUpContext) -> list[ExtractedClaim]:
        prompt = prepare_llm_prompt(
            self._prompt_template.replace(
                "{context_json}",
                build_claim_prompt_context(context),
            ),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        claims = parse_claims_response(raw_response)
        return FollowUpValidator.validate_claims(
            claims,
            answer_transcript=context.answer_transcript,
            question_text=context.question_text,
        )


def create_llm_claim_extractor(settings: Settings) -> LlmClaimExtractor:
    return LlmClaimExtractor(
        create_llm_provider(settings),
        model=settings.llm_model,
        disable_thinking=settings.llm_disable_thinking,
    )
