"""Parse LLM JSON responses into structured job description output."""

from app.features.job_description.processing.schemas import ParsedJobDescription
from app.shared.llm_json import parse_llm_payload


def parse_llm_json_response(raw_response: str) -> ParsedJobDescription:
    return parse_llm_payload(
        raw_response,
        ParsedJobDescription,
        error_message="LLM returned invalid job description JSON",
    )
