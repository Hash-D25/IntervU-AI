"""Hybrid resume parsing: rules first, LLM fills gaps."""

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.features.resume.parsing.json_response import parse_llm_json_response
from app.features.resume.parsing.pdf_text import extract_text_from_pdf
from app.features.resume.parsing.progress import ParseProgressCallback, run_with_progress_heartbeat
from app.features.resume.parsing.project_names import align_project_names, extract_project_names
from app.features.resume.parsing.prompt_utils import compact_partial_json, prepare_llm_prompt
from app.features.resume.parsing.schemas import ParsedResume
from app.features.resume.parsing.strategies.merge import merge_parsed
from app.features.resume.parsing.strategies.rule_extractor import RuleBasedResumeExtractor
from app.features.resume.parsing.text_trim import trim_resume_for_llm
from app.features.resume.parsing.validator import ParsedResumeValidator


class HybridResumeParser:
    name = "hybrid"

    def __init__(
        self,
        llm: LLMProvider,
        *,
        model: str,
        max_resume_chars: int,
        disable_thinking: bool,
        extractor: RuleBasedResumeExtractor | None = None,
    ) -> None:
        self._llm = llm
        self._model = model
        self._max_resume_chars = max_resume_chars
        self._disable_thinking = disable_thinking
        self._extractor = extractor or RuleBasedResumeExtractor()
        self._full_prompt = load_prompt("resume_parsing.txt")
        self._hybrid_prompt = load_prompt("resume_parsing_hybrid.txt")

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
        await report("rules", 45, "Extracting skills and keywords…")
        partial = self._extractor.extract(resume_text)

        if not self._extractor.needs_llm(partial):
            return ParsedResumeValidator.validate(partial)

        await report("llm", 55, "Running AI analysis…")
        llm_context = trim_resume_for_llm(resume_text, self._max_resume_chars)
        prompt = prepare_llm_prompt(
            self._build_prompt(llm_context, partial),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await run_with_progress_heartbeat(
            self._llm.generate([ChatMessage(role="user", content=prompt)]),
            on_progress=on_progress,
            stage="llm",
            start_percent=55,
            end_percent=84,
            message="Running AI analysis…",
        )
        await report("validating", 85, "Validating results…")
        llm_parsed = parse_llm_json_response(raw_response)
        merged = merge_parsed(partial, llm_parsed)
        merged = _align_projects_from_text(resume_text, merged)
        return ParsedResumeValidator.validate(merged)

    def _build_prompt(self, resume_text: str, partial: ParsedResume) -> str:
        if partial.skills or partial.technologies:
            return self._hybrid_prompt.replace(
                "{partial_json}", compact_partial_json(partial)
            ).replace("{resume_text}", resume_text)
        return self._full_prompt.replace("{resume_text}", resume_text)


def _align_projects_from_text(resume_text: str, parsed: ParsedResume) -> ParsedResume:
    reference = extract_project_names(resume_text)
    if not reference or not parsed.projects:
        return parsed
    return parsed.model_copy(
        update={"projects": align_project_names(reference, parsed.projects)}
    )


def create_hybrid_resume_parser(settings: Settings) -> HybridResumeParser:
    return HybridResumeParser(
        create_llm_provider(settings),
        model=settings.llm_model,
        max_resume_chars=settings.llm_max_resume_chars,
        disable_thinking=settings.llm_disable_thinking,
    )
