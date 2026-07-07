"""Build feedback context from interview history and evaluations."""

from app.features.feedback.schemas import EvaluatedAnswerSummary, FeedbackContext
from app.features.interview.execution.schemas import SessionContext, SessionQuestion
from app.features.interview.models import Interview
from app.features.interview.planning.schemas import InterviewMetadata


def build_feedback_context(interview: Interview) -> FeedbackContext:
    metadata = InterviewMetadata.model_validate(interview.interview_metadata)
    evaluated_answers = _evaluated_answers_from_execution(interview)
    if not evaluated_answers:
        raise ValueError("Interview has no evaluated answers")

    overall_average = round(
        sum(item.overall_score for item in evaluated_answers) / len(evaluated_answers),
        2,
    )
    dimension_averages = _dimension_averages(evaluated_answers)
    recurring_strengths = _recurring_phrases(
        [phrase for item in evaluated_answers for phrase in item.answer_strengths]
    )
    recurring_improvements = _recurring_phrases(
        [phrase for item in evaluated_answers for phrase in item.answer_improvements]
    )

    return FeedbackContext(
        company_name=metadata.company_name,
        target_role=metadata.target_role,
        interview_type=metadata.interview_type.value,
        evaluated_answers=evaluated_answers,
        overall_average_score=overall_average,
        dimension_averages=dimension_averages,
        recurring_strengths=recurring_strengths,
        recurring_improvements=recurring_improvements,
    )


def _evaluated_answers_from_execution(interview: Interview) -> list[EvaluatedAnswerSummary]:
    raw = interview.execution_context or {}
    if not raw:
        return []
    session = SessionContext.model_validate(raw)
    summaries: list[EvaluatedAnswerSummary] = []
    for question in session.questions:
        summary = _question_to_summary(question)
        if summary is not None:
            summaries.append(summary)
    return summaries


def _question_to_summary(question: SessionQuestion) -> EvaluatedAnswerSummary | None:
    if not question.answered or not question.answer_transcript or question.evaluation is None:
        return None
    return EvaluatedAnswerSummary(
        position=question.position,
        phase=question.phase.value,
        category=question.category,
        question_text=question.text,
        answer_transcript=question.answer_transcript,
        overall_score=question.evaluation.overall_score,
        dimension_scores=question.evaluation.scores,
        answer_strengths=question.evaluation.strengths,
        answer_improvements=question.evaluation.improvements,
    )


def _dimension_averages(answers: list[EvaluatedAnswerSummary]) -> dict[str, float]:
    totals: dict[str, float] = {}
    counts: dict[str, int] = {}
    for answer in answers:
        for score in answer.dimension_scores:
            key = score.dimension.value
            totals[key] = totals.get(key, 0.0) + score.score
            counts[key] = counts.get(key, 0) + 1
    return {
        key: round(totals[key] / counts[key], 2)
        for key in totals
        if counts.get(key, 0) > 0
    }


def _recurring_phrases(phrases: list[str], *, limit: int = 6) -> list[str]:
    cleaned = [phrase.strip() for phrase in phrases if phrase.strip()]
    if not cleaned:
        return []
    ordered: list[str] = []
    seen: set[str] = set()
    for phrase in cleaned:
        key = phrase.casefold()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(phrase)
        if len(ordered) >= limit:
            break
    return ordered


def weakest_dimensions(dimension_averages: dict[str, float], *, limit: int = 2) -> list[str]:
    if not dimension_averages:
        return []
    ordered = sorted(dimension_averages.items(), key=lambda item: item[1])
    return [name for name, _score in ordered[:limit]]


def strongest_dimensions(dimension_averages: dict[str, float], *, limit: int = 2) -> list[str]:
    if not dimension_averages:
        return []
    ordered = sorted(dimension_averages.items(), key=lambda item: item[1], reverse=True)
    return [name for name, _score in ordered[:limit]]
