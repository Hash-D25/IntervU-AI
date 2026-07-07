"""LLM-based resume parsing strategy."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.features.resume.parsing.json_response import parse_llm_json_response
from app.features.resume.parsing.pdf_text import extract_text_from_pdf
from app.features.resume.parsing.progress import ParseProgressCallback
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt
from app.features.resume.parsing.schemas import ParsedResume
from app.features.resume.parsing.text_trim import trim_resume_for_llm
from app.features.resume.parsing.validator import ParsedResumeValidator


class LlmResumeParser:
    name = "llm"

    def __init__(
        self,
        llm: LLMProvider,
        *,
        model: str,
        max_resume_chars: int,
        disable_thinking: bool,
    ) -> None:
        self._llm = llm
        self._model = model
        self._max_resume_chars = max_resume_chars
        self._disable_thinking = disable_thinking
        self._prompt_template = load_prompt("resume_parsing.txt")

    async def parse(
        self,
        pdf_bytes: bytes,
        *,
        on_progress: ParseProgressCallback | None = None,
    ) -> ParsedResume:
        async def report(stage: str, percent: int, message: str) -> None:
            if on_progress is not None:
                await on_progress(stage, percent, message)

        await report("extracting", 35, "Extracting text from PDF…")
        resume_text = extract_text_from_pdf(pdf_bytes)
        await report("llm", 55, "Running AI analysis…")
        llm_context = trim_resume_for_llm(resume_text, self._max_resume_chars)
        prompt = prepare_llm_prompt(
            self._prompt_template.replace("{resume_text}", llm_context),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        await report("validating", 85, "Validating results…")
        parsed = parse_llm_json_response(raw_response)
        return ParsedResumeValidator.validate(parsed)


def create_llm_resume_parser(settings: Settings) -> LlmResumeParser:
    return LlmResumeParser(
        create_llm_provider(settings),
        model=settings.llm_model,
        max_resume_chars=settings.llm_max_resume_chars,
        disable_thinking=settings.llm_disable_thinking,
    )
