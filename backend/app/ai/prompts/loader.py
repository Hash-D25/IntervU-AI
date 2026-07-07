"""Load prompt templates from the prompts directory."""

from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent


def load_prompt(filename: str) -> str:
    return (_PROMPTS_DIR / filename).read_text(encoding="utf-8")
