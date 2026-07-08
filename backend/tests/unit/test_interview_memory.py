"""Interview memory builder and prompt serialization tests."""

from uuid import uuid4

from app.features.evaluation.schemas import (
    AnswerEvaluationResult,
    DimensionScore,
    EvaluationDimension,
)
from app.features.interview.execution.schemas import (
    EngineStatus,
    InterviewPhase,
    SessionContext,
    SessionQuestion,
)
from app.features.interview.follow_up.prompt_context import build_follow_up_prompt_context
from app.features.interview.follow_up.schemas import ExtractedClaim, FollowUpContext
from app.features.interview.memory.builder import NoOpMemoryBuilder, SessionMemoryBuilder
from app.features.interview.memory.prompt_context import memory_prompt_payload
from app.features.interview.memory.schemas import InterviewMemory, MemoryAnswerSnippet
from app.features.interview.planning.schemas import InterviewPlan, InterviewType
from app.features.interview.question_generation.context_builder import build_prompt_context
from app.features.interview.question_generation.schemas import QuestionGenerationContext
from app.features.resume.parsing.schemas import ParsedResume


def _evaluation(*, overall: float = 7.0) -> AnswerEvaluationResult:
    return AnswerEvaluationResult(
        scores=[
            DimensionScore(dimension=dim, score=overall, rationale="ok")
            for dim in EvaluationDimension
        ],
        overall_score=overall,
        strengths=["Clear ownership"],
        improvements=["Explain tradeoffs"],
        evaluator_name="fake",
    )


def _answered_session() -> SessionContext:
    return SessionContext(
        status=EngineStatus.IN_PROGRESS,
        phase=InterviewPhase.CS_FUNDAMENTALS,
        interview_type=InterviewType.TECHNICAL,
        company_name="EPAM",
        target_role="SDE",
        phase_sequence=[InterviewPhase.PROJECTS, InterviewPhase.CS_FUNDAMENTALS],
        questions_per_phase={InterviewPhase.PROJECTS: 1, InterviewPhase.CS_FUNDAMENTALS: 1},
        questions=[
            SessionQuestion(
                id=uuid4(),
                position=0,
                phase=InterviewPhase.PROJECTS,
                text="How do you authenticate API requests?",
                category="project",
                difficulty="medium",
                expected_topics=["auth", "jwt"],
                answered=True,
                answer_transcript=(
                    "We issue JWT tokens after login and store sessions in Redis for "
                    "fast validation on UncDoIt."
                ),
                evaluation=_evaluation(),
                probed_claims=["JWT tokens"],
            ),
            SessionQuestion(
                id=uuid4(),
                position=1,
                phase=InterviewPhase.CS_FUNDAMENTALS,
                text="Explain REST rate limiting.",
                category="cs_fundamentals",
                difficulty="medium",
                expected_topics=["rate limiting"],
                answered=False,
            ),
        ],
    )


def test_session_memory_builder_captures_answers_topics_and_strengths() -> None:
    memory = SessionMemoryBuilder().rebuild(_answered_session())

    assert memory.updated_from_question_count == 1
    assert len(memory.answers) == 1
    assert "JWT" in memory.answers[0].answer_excerpt or "jwt" in memory.topics_covered[0].casefold()
    assert any("jwt" in topic.casefold() for topic in memory.topics_covered)
    assert "Clear ownership" in memory.strengths
    assert "Explain tradeoffs" in memory.weak_areas
    assert "overall" in memory.dimension_averages


def test_noop_memory_builder_returns_empty() -> None:
    memory = NoOpMemoryBuilder().rebuild(_answered_session())
    assert memory.updated_from_question_count == 0
    assert memory.answers == []


def test_memory_prompt_payload_none_when_empty() -> None:
    assert memory_prompt_payload(None) is None
    assert memory_prompt_payload(InterviewMemory()) is None


def test_question_prompt_context_includes_interview_memory() -> None:
    memory = SessionMemoryBuilder().rebuild(_answered_session())
    context = QuestionGenerationContext(
        company_name="EPAM",
        target_role="SDE",
        interview_type=InterviewType.TECHNICAL,
        interview_plan=InterviewPlan(
            focus_areas=["backend"],
            question_mix=["cs_fundamentals"],
            estimated_rounds=2,
            follow_up_strategy="Probe claims.",
            evaluation_axes=["depth"],
        ),
        resume=ParsedResume(),
        execution_phase=InterviewPhase.CS_FUNDAMENTALS,
        phase_instruction="Ask one CS fundamentals question.",
        memory=memory,
    )
    payload = build_prompt_context(context)
    assert "interview_memory" in payload
    assert "You mentioned JWT earlier" in payload


def test_follow_up_prompt_context_includes_interview_memory() -> None:
    memory = InterviewMemory(
        answers=[
            MemoryAnswerSnippet(
                position=0,
                phase="projects",
                category="project",
                question_text="Auth?",
                answer_excerpt="We use JWT.",
                key_claims=["JWT"],
            )
        ],
        notable_mentions=["JWT"],
        updated_from_question_count=1,
    )
    context = FollowUpContext(
        company_name="EPAM",
        target_role="SDE",
        phase=InterviewPhase.PROJECTS,
        category="project",
        question_text="How do you cache?",
        answer_transcript="We use Redis.",
        memory=memory,
    )
    payload = build_follow_up_prompt_context(
        context,
        [ExtractedClaim(text="We use Redis.", probe_angle="Why Redis?")],
    )
    assert "interview_memory" in payload
    assert "JWT" in payload
