"""Keep only claims that are grounded in the answer transcript."""

import re

_WORD = re.compile(r"[a-z0-9+.#]+", re.IGNORECASE)
_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "been",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "into",
        "is",
        "it",
        "its",
        "no",
        "not",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "were",
        "with",
        "without",
    }
)


def claim_grounded_in_answer(claim_text: str, answer_transcript: str, question_text: str) -> bool:
    """Return True when claim content is supported by the answer, not only the question."""
    claim_tokens = _meaningful_tokens(claim_text)
    if not claim_tokens:
        return False

    answer_tokens = set(_meaningful_tokens(answer_transcript))
    question_tokens = set(_meaningful_tokens(question_text))

    answer_overlap = claim_tokens & answer_tokens
    question_only = claim_tokens & question_tokens - answer_tokens

    if not answer_overlap:
        return False

    # Premise-leak: claim is mostly question wording with negligible answer support.
    if len(question_only) >= 2 and len(answer_overlap) <= 1:
        return False
    return not (len(answer_overlap) / len(claim_tokens) < 0.34 and question_only)


def _meaningful_tokens(text: str) -> set[str]:
    return {
        token.casefold()
        for token in _WORD.findall(text)
        if len(token) > 1 and token.casefold() not in _STOPWORDS
    }
