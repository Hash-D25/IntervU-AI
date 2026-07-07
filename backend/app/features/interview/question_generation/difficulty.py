"""Infer question difficulty from job description seniority."""

from app.features.interview.question_generation.schemas import Difficulty
from app.features.job_description.processing.seniority import SeniorityLevel


def infer_difficulty(seniority: SeniorityLevel | None) -> Difficulty:
    if seniority in {SeniorityLevel.INTERN, SeniorityLevel.ENTRY, None}:
        return Difficulty.EASY
    if seniority in {SeniorityLevel.JUNIOR, SeniorityLevel.MID}:
        return Difficulty.MEDIUM
    return Difficulty.HARD
