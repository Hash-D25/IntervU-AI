"""Extract and align exact project names from resume text."""

import re

from app.features.resume.parsing.schemas import ProjectEntry

_PROJECTS_HEADER = re.compile(r"(?im)^projects?\s*:?\s*$")
_LINK_SUFFIX = re.compile(
    r"\s+(Link|Live|Code|Extension)(\s*[|]\s*(Link|Live|Code|Extension))*\s*$",
    re.IGNORECASE,
)
_BULLET_LINE = re.compile(r"^[\-*•·∗]\s+(.+)$")
_DESCRIPTION_START = re.compile(
    r"^(?:built|developed|designed|implemented|created|worked|led|maintained|optimized)\b",
    re.IGNORECASE,
)
_SECTION_BREAK = re.compile(
    r"^(?:experience|work experience|employment|education|skills|technical skills|"
    r"achievements|awards|honors|summary|objective|certifications|technologies)\b",
    re.IGNORECASE,
)
_TITLE_SEP = re.compile(r"(?:\s[-–-]\s+|:\s)")
_FORMATTING = re.compile(r"[*_]+")
_OCR_SPLIT = re.compile(r"\b([A-Z])\s+([a-z]{2,})\b")
_MERGED_OCR = re.compile(r"\b([A-Z])\s+([a-z]{1,3})(?=[A-Z])")
_CAP_SPLIT = re.compile(r"([a-z])([A-Z])\s+([a-z]{2,})")
_MULTI_SPACE = re.compile(r"\s+")


def extract_project_names(text: str) -> list[ProjectEntry]:
    lines = text.splitlines()
    names: list[str] = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if _PROJECTS_HEADER.match(stripped):
            in_section = True
            continue
        if in_section and _SECTION_BREAK.match(stripped):
            break
        if not in_section:
            continue
        if _BULLET_LINE.match(stripped):
            continue
        if _DESCRIPTION_START.match(stripped):
            continue
        name = _clean_title_line(stripped)
        if not _looks_like_project_title(name, raw_line=stripped):
            continue
        names.append(name)

    return [ProjectEntry(name=name) for name in names]


def align_project_names(
    reference: list[ProjectEntry], projects: list[ProjectEntry]
) -> list[ProjectEntry]:
    if not reference or not projects:
        return projects

    ref_names = [entry.name for entry in reference]
    used_refs: set[int] = set()
    aligned: list[ProjectEntry] = []

    for index, project in enumerate(projects):
        matched_idx = _best_name_match(project.name, ref_names, used_refs)
        if matched_idx is None and len(reference) == len(projects):
            matched_idx = index if index not in used_refs else None
        if matched_idx is not None:
            used_refs.add(matched_idx)
            name = ref_names[matched_idx]
        else:
            name = project.name
        aligned.append(project.model_copy(update={"name": sanitize_project_name(name)}))

    return aligned


def align_question_text(text: str, project_names: list[str]) -> str:
    """Replace noisy project-name variants in generated question text."""
    if not text or not project_names:
        return text

    canonical = sorted(
        {sanitize_project_name(name) for name in project_names if name.strip()},
        key=len,
        reverse=True,
    )
    result = text
    for name in canonical:
        marker = _project_marker(name)
        if not marker or marker.lower() not in result.lower():
            continue
        pattern = re.compile(
            re.escape(marker) + r"[\w\s:.\-–-]{0,140}?(?="
            r"[?.!,;)]|\s+(?:and|or|versus|vs\.?|with|using|in|for|that|where|when)\b|$)",
            re.IGNORECASE,
        )

        def _replacer(match: re.Match[str], *, canonical_name: str = name) -> str:
            fragment = match.group(0).strip()
            cleaned = sanitize_project_name(fragment)
            name_key = _name_match_key(canonical_name)
            cleaned_key = _name_match_key(cleaned)
            if (
                cleaned_key == name_key
                or name_key in cleaned_key
                or cleaned_key in name_key
            ):
                return canonical_name
            return fragment

        result = pattern.sub(_replacer, result)
        result = re.sub(
            re.escape(name) + r"\s+Link\b",
            name,
            result,
            flags=re.IGNORECASE,
        )
    return _MULTI_SPACE.sub(" ", result).strip()


def normalize_project_references_in_text(text: str, project_names: list[str]) -> str:
    """Align, normalize dash variants, and unwrap quoted project names."""
    if not text or not project_names:
        return text

    result = align_question_text(text, project_names)
    canonical = sorted(
        {sanitize_project_name(name) for name in project_names if name.strip()},
        key=len,
        reverse=True,
    )
    for name in canonical:
        result = _normalize_dash_variants(result, name)
        for quote in ("'", '"'):
            result = result.replace(f"{quote}{name}{quote}", name)
        result = _dedupe_adjacent_project_mentions(result, name)
    return _MULTI_SPACE.sub(" ", result).strip()


def _dedupe_adjacent_project_mentions(text: str, canonical: str) -> str:
    """Collapse duplicated project titles like '... Viewer in Viewer'."""
    escaped = re.escape(canonical)
    # Same title repeated with 'in'/'for'/'of' between.
    pattern = re.compile(
        rf"\b({escaped})\s+(?:in|for|of|on|at)\s+\1\b",
        re.IGNORECASE,
    )
    result = pattern.sub(r"\1", text)
    # Back-to-back duplicate titles.
    adjacent = re.compile(rf"\b({escaped})(?:\s+\1)+\b", re.IGNORECASE)
    return adjacent.sub(r"\1", result)


def _normalize_dash_variants(text: str, canonical: str) -> str:
    if " - " in canonical:
        left, right = canonical.split(" - ", 1)
        pattern = re.compile(
            re.escape(left) + r"\s*[-–-]\s*" + re.escape(right),
            re.IGNORECASE,
        )
        return pattern.sub(canonical, text)
    if ": " in canonical:
        left, right = canonical.split(": ", 1)
        pattern = re.compile(
            re.escape(left) + r"\s*:\s*" + re.escape(right),
            re.IGNORECASE,
        )
        return pattern.sub(canonical, text)
    return text


def project_marker(name: str) -> str:
    return _project_marker(name)


def name_match_key(name: str) -> str:
    return _name_match_key(name)


def _project_marker(name: str) -> str:
    for sep in (" - ", ": ", ":"):
        if sep in name:
            return name.split(sep, 1)[0].strip()
    words = name.split()
    return words[0] if words else name


def _best_name_match(name: str, references: list[str], used: set[int]) -> int | None:
    key = _name_match_key(name)
    best_idx: int | None = None
    best_score = 0
    for idx, ref in enumerate(references):
        if idx in used:
            continue
        ref_key = _name_match_key(ref)
        if key == ref_key:
            return idx
        if key in ref_key or ref_key in key:
            score = len(ref)
            if score > best_score:
                best_score = score
                best_idx = idx
    return best_idx


def sanitize_project_name(name: str) -> str:
    """Normalize project titles for display and interview context."""
    cleaned = _FORMATTING.sub("", name).strip()
    cleaned = _fix_ocr_spacing(cleaned)
    while True:
        stripped = re.sub(r"\s+(?:Link|Live|Code)\s*$", "", cleaned, flags=re.IGNORECASE)
        if stripped == cleaned:
            break
        cleaned = stripped.strip()
    cleaned = re.sub(
        r"(?<=[a-z])Live(?:\s+Extension)?\s*$", "", cleaned, flags=re.IGNORECASE
    ).strip()
    cleaned = re.sub(r"\s+Live\s+Extension\s*$", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"(?<=[a-z])Link\s*$", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"(?<=[a-z])Live\s*$", "", cleaned, flags=re.IGNORECASE).strip()
    return _MULTI_SPACE.sub(" ", cleaned).strip()


def _clean_title_line(line: str) -> str:
    return sanitize_project_name(line)


def _fix_ocr_spacing(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = _MERGED_OCR.sub(r"\1\2", text)
        text = _CAP_SPLIT.sub(r"\1\2\3", text)
        text = _OCR_SPLIT.sub(r"\1\2", text)
    return text


def _name_match_key(name: str) -> str:
    key = re.sub(r"\s+", " ", name.strip().casefold())
    key = re.sub(r"\s*:\s*", ": ", key)
    key = re.sub(r"\s*[-–-]\s*", " - ", key)
    return key


def _looks_like_project_title(line: str, *, raw_line: str | None = None) -> bool:
    if len(line) < 3 or len(line) > 180:
        return False
    if _DESCRIPTION_START.match(line):
        return False
    if line.startswith("http") or line.count("/") > 3:
        return False
    if raw_line and _LINK_SUFFIX.search(raw_line):
        return True
    if line.count(",") >= 2:
        return False
    if _TITLE_SEP.search(line):
        return True
    words = line.split()
    return (
        line[0].isupper()
        and not line.endswith(".")
        and len(words) <= 8
        and "," not in line
    )
