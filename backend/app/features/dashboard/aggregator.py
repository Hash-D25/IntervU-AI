"""Aggregate interview and feedback data for the dashboard."""

from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime

from app.features.dashboard.schemas import (
    CategoryScore,
    DashboardSummary,
    ProgressPoint,
)
from app.features.feedback.context_builder import evaluated_answers_from_interview
from app.features.feedback.models import FeedbackReport
from app.features.feedback.schemas import EvaluatedAnswerSummary
from app.features.interview.mapper import to_interview_history_item
from app.features.interview.models import Interview, InterviewStatus


def build_dashboard_summary(interviews: Sequence[Interview]) -> DashboardSummary:
    history = []
    all_answers: list[EvaluatedAnswerSummary] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    progress: list[ProgressPoint] = []

    for interview in interviews:
        answers = evaluated_answers_from_interview(interview)
        all_answers.extend(answers)
        report = interview.feedback_report
        overall = _overall_score(interview, report, answers)
        history.append(to_interview_history_item(interview))
        if report is not None:
            strengths.extend(report.strengths)
            weaknesses.extend(report.weaknesses)
        if overall is not None:
            progress.append(
                ProgressPoint(
                    interview_id=interview.id,
                    label=_progress_label(interview),
                    recorded_at=_progress_timestamp(interview),
                    overall_score=overall,
                )
            )

    progress.sort(key=lambda point: point.recorded_at)
    completed = sum(1 for item in history if item.status == InterviewStatus.COMPLETED)

    return DashboardSummary(
        interview_history=history,
        strengths=_dedupe_phrases(strengths),
        weaknesses=_dedupe_phrases(weaknesses),
        category_scores=_category_scores(all_answers),
        dimension_averages=_dimension_averages(all_answers),
        progress_over_time=progress,
        total_interviews=len(history),
        completed_interviews=completed,
    )


def _overall_score(
    interview: Interview,
    report: FeedbackReport | None,
    answers: list[EvaluatedAnswerSummary],
) -> float | None:
    if report is not None:
        return round(report.overall_score, 2)
    if not answers:
        return None
    return round(sum(item.overall_score for item in answers) / len(answers), 2)


def _progress_label(interview: Interview) -> str:
    company = (interview.company or "").strip()
    role = interview.role.strip()
    if company and role:
        return f"{company} - {role}"
    return company or role or "Interview"


def _progress_timestamp(interview: Interview) -> datetime:
    if interview.status == InterviewStatus.COMPLETED:
        return interview.updated_at
    return interview.created_at


def _category_scores(answers: list[EvaluatedAnswerSummary]) -> list[CategoryScore]:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for answer in answers:
        key = answer.category.strip().lower()
        if not key:
            continue
        totals[key] += answer.overall_score
        counts[key] += 1
    items = [
        CategoryScore(
            category=category,
            average_score=round(totals[category] / counts[category], 2),
            answer_count=counts[category],
        )
        for category in sorted(totals)
    ]
    return sorted(items, key=lambda item: item.average_score, reverse=True)


def _dimension_averages(answers: list[EvaluatedAnswerSummary]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for answer in answers:
        for score in answer.dimension_scores:
            key = score.dimension.value
            totals[key] += score.score
            counts[key] += 1
    return {
        key: round(totals[key] / counts[key], 2)
        for key in sorted(totals)
        if counts[key] > 0
    }


def _dedupe_phrases(phrases: list[str], *, limit: int = 10) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for phrase in phrases:
        cleaned = phrase.strip()
        if not cleaned:
            continue
        key = cleaned.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(cleaned)
        if len(ordered) >= limit:
            break
    return ordered
