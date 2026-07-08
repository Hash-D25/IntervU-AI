"""Map configured format names to HTTP audio content types."""

from pathlib import Path

from app.core.exceptions import BadRequestError

_FORMAT_TO_CONTENT_TYPES: dict[str, frozenset[str]] = {
    "wav": frozenset({"audio/wav", "audio/x-wav"}),
    "mp3": frozenset({"audio/mpeg", "audio/mp3", "audio/x-mpeg"}),
    "m4a": frozenset(
        {
            "audio/mp4",
            "audio/x-m4a",
            "audio/m4a",
            "audio/mp4a-latm",
            "video/mp4",
        }
    ),
    "webm": frozenset({"audio/webm", "video/webm"}),
    "ogg": frozenset({"audio/ogg", "application/ogg"}),
}

_CANONICAL_CONTENT_TYPES: dict[str, str] = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "m4a": "audio/mp4",
    "webm": "audio/webm",
    "ogg": "audio/ogg",
}

_EXTENSION_TO_FORMAT: dict[str, str] = {
    ".wav": "wav",
    ".mp3": "mp3",
    ".m4a": "m4a",
    ".webm": "webm",
    ".ogg": "ogg",
}

_GENERIC_CONTENT_TYPES = frozenset({"application/octet-stream", "binary/octet-stream"})


def parse_supported_audio_formats(raw: str) -> frozenset[str]:
    content_types: set[str] = set()
    for name in raw.split(","):
        key = name.strip().lower()
        if not key:
            continue
        canonical = _CANONICAL_CONTENT_TYPES.get(key)
        if canonical is not None:
            content_types.add(canonical)
    if not content_types:
        return frozenset(_CANONICAL_CONTENT_TYPES.values())
    return frozenset(content_types)


def supported_format_labels(content_types: frozenset[str]) -> str:
    labels: list[str] = []
    for name, canonical in _CANONICAL_CONTENT_TYPES.items():
        if canonical in content_types:
            labels.append(name)
    return ", ".join(labels)


def resolve_upload_content_type(
    content_type: str | None,
    filename: str | None,
    *,
    supported_content_types: frozenset[str],
) -> str:
    normalized = _normalize_content_type(content_type)
    extension = Path(filename or "").suffix.lower()
    format_name = _EXTENSION_TO_FORMAT.get(extension)

    if normalized in supported_content_types:
        return normalized

    alias_format = _format_for_alias(normalized, extension)
    if alias_format is not None:
        canonical = _CANONICAL_CONTENT_TYPES[alias_format]
        if canonical in supported_content_types:
            return canonical

    if (normalized in _GENERIC_CONTENT_TYPES or normalized is None) and format_name is not None:
        canonical = _CANONICAL_CONTENT_TYPES[format_name]
        if canonical in supported_content_types:
            return canonical

    raise BadRequestError(
        "Unsupported audio format. Upload one of: "
        f"{supported_format_labels(supported_content_types)}."
    )


def _normalize_content_type(content_type: str | None) -> str | None:
    if not content_type:
        return None
    return content_type.split(";", 1)[0].strip().lower()


def _format_for_alias(content_type: str, extension: str) -> str | None:
    for format_name, aliases in _FORMAT_TO_CONTENT_TYPES.items():
        if content_type not in aliases:
            continue
        if format_name == "m4a" and content_type == "video/mp4" and extension != ".m4a":
            continue
        return format_name
    return None
