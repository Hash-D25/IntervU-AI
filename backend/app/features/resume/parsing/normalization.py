"""Normalize and deduplicate parsed resume string lists."""

import re

_BULLET_PREFIX = re.compile(r"^[\s\-*•·∗]+")
_MULTI_SPACE = re.compile(r"\s+")
_CATEGORY_LINE = re.compile(
    r"^(?:languages?|frameworks?(?:/libraries)?|database|tools?|concepts?|"
    r"java technologies|other skills?)\s*:\s*(.+)$",
    re.IGNORECASE,
)

_CANONICAL_KEYS: dict[str, str] = {
    "postgres": "postgresql",
    "nodejs": "node.js",
    "nextjs": "next.js",
}


def normalize_list_item(value: str) -> str:
    item = _BULLET_PREFIX.sub("", value.strip())
    item = _MULTI_SPACE.sub(" ", item)
    return item.strip()


def dedupe_key(value: str) -> str:
    key = normalize_list_item(value).casefold()
    return _CANONICAL_KEYS.get(key, key)


def fuzzy_dedupe_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize_list_item(value).casefold())


def split_list_values(raw: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in raw:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(depth - 1, 0)
        if char == "," and depth == 0:
            part = "".join(current).strip()
            if part:
                parts.append(part)
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    if not parts:
        return [item.strip() for item in re.split(r"[,|;/]+", raw) if item.strip()]
    return parts


def normalize_string_list(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        cleaned = normalize_list_item(value)
        if not cleaned:
            continue
        category_match = _CATEGORY_LINE.match(cleaned)
        if category_match:
            for part in split_list_values(category_match.group(1)):
                item = normalize_list_item(part)
                if item:
                    _append_unique(normalized, seen, item, dedupe_key)
            continue
        _append_unique(normalized, seen, cleaned, dedupe_key)
    return normalized


def normalize_achievements(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        cleaned = normalize_list_item(value)
        if not cleaned:
            continue
        _append_unique(normalized, seen, cleaned, fuzzy_dedupe_key)
    return normalized


def subtract_overlap(primary: list[str], secondary: list[str]) -> list[str]:
    primary_keys = {dedupe_key(item) for item in primary}
    result: list[str] = []
    seen: set[str] = set()
    for value in secondary:
        cleaned = normalize_list_item(value)
        if not cleaned:
            continue
        key = dedupe_key(cleaned)
        if key in primary_keys or key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
    return result


def _append_unique(
    items: list[str],
    seen: set[str],
    value: str,
    key_fn: object,
) -> None:
    key = key_fn(value)  # type: ignore[operator]
    if key in seen:
        return
    seen.add(key)
    items.append(value)
