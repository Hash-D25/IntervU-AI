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
_TITLE_SEP = re.compile(r"(?:\s[-–—]\s+|:\s)")
_FORMATTING = re.compile(r"[*_]+")


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
        aligned.append(project.model_copy(update={"name": name}))

    return aligned


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


def _clean_title_line(line: str) -> str:
    cleaned = _FORMATTING.sub("", line).strip()
    return _LINK_SUFFIX.sub("", cleaned).strip()


def _name_match_key(name: str) -> str:
    key = re.sub(r"\s+", " ", name.strip().casefold())
    key = re.sub(r"\s*:\s*", ": ", key)
    key = re.sub(r"\s*-\s*", " - ", key)
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
