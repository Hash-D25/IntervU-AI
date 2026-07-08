"""LLM-based transcript cleanup for speech-to-text errors."""

import json

from app.ai.prompts.loader import load_prompt
from app.ai.providers.base import ChatMessage, LLMProvider
from app.ai.providers.factory import create_llm_provider
from app.core.config import Settings
from app.core.exceptions import ParseError
from app.features.resume.parsing.prompt_utils import prepare_llm_prompt
from app.features.voice.schemas import TranscriptionContext
from app.shared.llm_json import extract_json_payload


class LlmTranscriptRefiner:
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
        self._prompt_template = load_prompt("transcript_refinement.txt")

    async def refine(self, transcript: str, *, context: TranscriptionContext) -> str:
        if not transcript.strip():
            return transcript
        prompt = prepare_llm_prompt(
            self._prompt_template.replace("{context_json}", _context_json(context))
            .replace("{raw_transcript}", transcript.strip()),
            model=self._model,
            disable_thinking=self._disable_thinking,
        )
        raw_response = await self._llm.generate([ChatMessage(role="user", content=prompt)])
        return _parse_refined_transcript(raw_response, fallback=transcript)


def create_llm_transcript_refiner(settings: Settings) -> LlmTranscriptRefiner:
    return LlmTranscriptRefiner(
        create_llm_provider(settings),
        model=settings.llm_model,
        disable_thinking=settings.llm_disable_thinking,
    )


def _context_json(context: TranscriptionContext) -> str:
    payload = {
        "company_name": context.company_name,
        "target_role": context.target_role,
        "hint_terms": context.hint_terms,
    }
    return json.dumps(payload, separators=(",", ":"))


def _parse_refined_transcript(raw_response: str, *, fallback: str) -> str:
    try:
        payload = json.loads(extract_json_payload(raw_response))
        transcript = str(payload.get("transcript", "")).strip()
        if not transcript:
            raise ParseError("Refiner returned empty transcript")
        return transcript
    except (json.JSONDecodeError, ParseError, ValueError):
        cleaned = raw_response.strip()
        if cleaned.startswith("{") or cleaned.startswith("["):
            return fallback
        return cleaned or fallback
