"""Remove improvement suggestions that contradict the answer transcript."""

import re

_QUANTIFY_GPA = re.compile(
    r"\b(?:quantif|provide|include|mention|add|state)\b.{0,30}\b(?:cgpa|gpa)\b",
    re.IGNORECASE,
)
_MENTION_PROJECTS = re.compile(
    r"\b(?:mention|include|talk about|discuss|share)\b.{0,30}\bprojects?\b",
    re.IGNORECASE,
)
_MENTION_MOTIVATION = re.compile(
    r"\b(?:explain|mention|clarify|state)\b.{0,40}\b"
    r"(?:why|interest|motivat|epam|company|role)\b",
    re.IGNORECASE,
)
_ANSWER_HAS_CP_COUNT = re.compile(
    r"\b\d{2,}\+?\s*(?:problems?|questions?)\b|"
    r"\bsolved\s+\d{2,}\+?\b|"
    r"\b\d{2,}\+?\s+on\s+(?:leetcode|codeforces)\b",
    re.IGNORECASE,
)
_ANSWER_HAS_GPA = re.compile(r"\b(?:cgpa|gpa)\b", re.IGNORECASE)
_ANSWER_HAS_PROJECTS = re.compile(
    r"\b(?:uncdoit|ytnotes|projects?|built|developed)\b",
    re.IGNORECASE,
)
_ANSWER_HAS_MOTIVATION = re.compile(
    r"\b(?:interested in|excited about|why).{0,60}\b(?:epam|role|internship|opportunity)\b",
    re.IGNORECASE,
)
_ASK_CP_CONTEXT = re.compile(
    r"\b(?:provide|explain|more context|develop|context about)\b.{0,60}\b"
    r"(?:competitive programming|analytical thinking|data structures|algorithms|dsa)\b",
    re.IGNORECASE,
)
_ANSWER_HAS_CP_TOPIC = re.compile(
    r"\b(?:competitive programming|leetcode|codeforces|data structures)\b",
    re.IGNORECASE,
)
_ASK_AUTH_DETAILS = re.compile(
    r"\b(?:more detailed|specifics|elaborate|offer).{0,50}\b(?:auth|authentication)\b",
    re.IGNORECASE,
)
_ANSWER_HAS_AUTH = re.compile(
    r"\b(?:auth|authentication|jwt|refresh flow|prisma)\b",
    re.IGNORECASE,
)

def filter_contradictory_improvements(
    improvements: list[str],
    answer_transcript: str,
) -> list[str]:
    if not improvements:
        return improvements
    answer = answer_transcript.strip()
    if not answer:
        return improvements

    filtered: list[str] = []
    for item in improvements:
        if _contradicts_answer(item, answer):
            continue
        filtered.append(item)
    return filtered


def _contradicts_answer(improvement: str, answer: str) -> bool:
    imp = improvement.casefold()
    if _asks_for_cp_quantification(imp) and _ANSWER_HAS_CP_COUNT.search(answer):
        return True
    if _ASK_CP_CONTEXT.search(improvement) and (
        _ANSWER_HAS_CP_COUNT.search(answer) or _ANSWER_HAS_CP_TOPIC.search(answer)
    ):
        return True
    if _ASK_AUTH_DETAILS.search(improvement) and _ANSWER_HAS_AUTH.search(answer):
        return True
    if (
        _asks_epam_project_alignment(improvement)
        and _ANSWER_HAS_MOTIVATION.search(answer)
        and _ANSWER_HAS_PROJECTS.search(answer)
    ):
        return True
    if _QUANTIFY_GPA.search(improvement) and _ANSWER_HAS_GPA.search(answer):
        return True
    if _MENTION_PROJECTS.search(improvement) and _ANSWER_HAS_PROJECTS.search(answer):
        return True
    return bool(
        _MENTION_MOTIVATION.search(improvement) and _ANSWER_HAS_MOTIVATION.search(answer)
    )


def _asks_for_cp_quantification(improvement: str) -> bool:
    mentions_cp = any(
        token in improvement
        for token in ("leetcode", "codeforces", "competitive programming", "problem")
    )
    asks_quantify = any(
        token in improvement
        for token in (
            "quantif",
            "number of",
            "how many",
            "add metrics",
            "specific numbers",
            "such as the number",
        )
    )
    return mentions_cp and asks_quantify


def _asks_epam_project_alignment(improvement: str) -> bool:
    imp = improvement.casefold()
    return "epam" in imp and "project" in imp and ("align" in imp or "alignment" in imp)
