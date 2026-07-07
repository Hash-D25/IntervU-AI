"""LLM-based job description analysis strategy."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.features.job_description.processing.json_response import parse_llm_json_response
from app.features.job_description.processing.schemas import ParsedJobDescription
from app.features.job_description.processing.text_trim import trim_job_description_for_llm
from app.features.job_description.processing.validator import ParsedJobDescriptionValidator
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt


class LlmJobDescriptionAnalyzer:
    name = "llm"

    def __init__(
        self,
        llm: LLMProvider,
        *,
        model: str,
        max_jd_chars: int,
        disable_thinking: bool,
    ) -> None:
        self._llm = llm
        self._model = model
        self._max_jd_chars = max_jd_chars
        self._disable_thinking = disable_thinking
        self._prompt_template = load_prompt("job_description_processing.txt")

    async def analyze(self, text: str) -> ParsedJobDescription:
        llm_context = trim_job_description_for_llm(text, self._max_jd_chars)
        prompt = prepare_llm_prompt(
            self._prompt_template.replace("{job_description_text}", llm_context),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        parsed = parse_llm_json_response(raw_response)
        return ParsedJobDescriptionValidator.validate(parsed)


def create_llm_job_description_analyzer(settings: Settings) -> LlmJobDescriptionAnalyzer:
    return LlmJobDescriptionAnalyzer(
        create_llm_provider(settings),
        model=settings.llm_model,
        max_jd_chars=settings.llm_max_jd_chars,
        disable_thinking=settings.llm_disable_thinking,
    )
