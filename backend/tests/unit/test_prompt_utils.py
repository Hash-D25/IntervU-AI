"""Prompt helper unit tests."""

from app.features.resume.parsing.prompt_utils import prepare_llm_prompt


def test_prepare_llm_prompt_disables_qwen_thinking() -> None:
    prompt = prepare_llm_prompt("Parse this resume.", model="qwen3:8b", disable_thinking=True)
    assert prompt.startswith("/no_think")


def test_prepare_llm_prompt_leaves_other_models_unchanged() -> None:
    prompt = prepare_llm_prompt("Parse this resume.", model="llama3.1:8b", disable_thinking=True)
    assert prompt == "Parse this resume."
