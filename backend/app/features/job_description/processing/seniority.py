"""Seniority level enum and normalization."""

import re
from enum import StrEnum

_MULTI_SPACE = re.compile(r"\s+")


class SeniorityLevel(StrEnum):
    INTERN = "intern"
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    STAFF = "staff"
    PRINCIPAL = "principal"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"
    UNSPECIFIED = "unspecified"


_SENIORITY_ALIASES = {
    "intern": SeniorityLevel.INTERN,
    "internship": SeniorityLevel.INTERN,
    "entry": SeniorityLevel.ENTRY,
    "entry-level": SeniorityLevel.ENTRY,
    "entry level": SeniorityLevel.ENTRY,
    "graduate": SeniorityLevel.ENTRY,
    "junior": SeniorityLevel.JUNIOR,
    "jr": SeniorityLevel.JUNIOR,
    "associate": SeniorityLevel.JUNIOR,
    "mid": SeniorityLevel.MID,
    "mid-level": SeniorityLevel.MID,
    "mid level": SeniorityLevel.MID,
    "intermediate": SeniorityLevel.MID,
    "senior": SeniorityLevel.SENIOR,
    "sr": SeniorityLevel.SENIOR,
    "lead": SeniorityLevel.LEAD,
    "team lead": SeniorityLevel.LEAD,
    "staff": SeniorityLevel.STAFF,
    "principal": SeniorityLevel.PRINCIPAL,
    "manager": SeniorityLevel.MANAGER,
    "engineering manager": SeniorityLevel.MANAGER,
    "director": SeniorityLevel.DIRECTOR,
    "executive": SeniorityLevel.EXECUTIVE,
    "vp": SeniorityLevel.EXECUTIVE,
    "unspecified": SeniorityLevel.UNSPECIFIED,
    "unknown": SeniorityLevel.UNSPECIFIED,
}


def normalize_seniority_level(value: SeniorityLevel | str) -> SeniorityLevel:
    if isinstance(value, SeniorityLevel):
        return value
    key = _MULTI_SPACE.sub(" ", str(value).strip().casefold())
    if key in _SENIORITY_ALIASES:
        return _SENIORITY_ALIASES[key]
    for alias, level in _SENIORITY_ALIASES.items():
        if alias in key:
            return level
    try:
        return SeniorityLevel(key.replace("_", "-"))
    except ValueError:
        return SeniorityLevel.UNSPECIFIED
