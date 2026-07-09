"""Parse LLM JSON responses into structured resume output."""

from app.features.resume.parsing.schemas import ParsedResume
from app.shared.llm_json import parse_llm_payload


def parse_llm_json_response(raw_response: str) -> ParsedResume:
    return parse_llm_payload(
        raw_response,
        ParsedResume,
        error_message="LLM returned invalid resume JSON",
    )
