"""Follow-up service unit tests."""

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
from app.features.interview.follow_up.schemas import (
    ExtractedClaim,
    FollowUpContext,
    GeneratedFollowUp,
)
from app.features.interview.follow_up.service import FollowUpService, parse_allowed_phases
from app.features.interview.planning.schemas import InterviewPlan, InterviewType


class FakeClaimExtractor:
    name = "fake"

    async def extract(self, context: FollowUpContext) -> list[ExtractedClaim]:
        return [
            ExtractedClaim(
                text="We used Redis.",
                claim_type="technology",
                probe_angle="Why Redis versus other caches",
            )
        ]


class FakeFollowUpGenerator:
    name = "fake"

    async def generate(
        self,
        context: FollowUpContext,
        *,
        claims: list[ExtractedClaim],
    ) -> GeneratedFollowUp | None:
        return GeneratedFollowUp(
            text="Why Redis instead of Memcached?",
            category=context.category,
            difficulty="medium",
            expected_topics=["caching", "tradeoffs"],
            evaluation_rubric=["depth", "reasoning"],
            probed_claims=[claim.text for claim in claims],
            generator_name=self.name,
        )


def _plan() -> InterviewPlan:
    return InterviewPlan(
        focus_areas=["backend"],
        question_mix=["project"],
        estimated_rounds=2,
        follow_up_strategy="Probe resume-backed claims.",
        evaluation_axes=["depth"],
    )


def _session_with_answered_project() -> tuple[SessionContext, SessionQuestion]:
    question_id = uuid4()
    question = SessionQuestion(
        id=question_id,
        position=0,
        phase=InterviewPhase.PROJECTS,
        text="Tell me about your caching approach.",
        category="project",
        difficulty="medium",
        expected_topics=["caching"],
        evaluation_rubric=["depth"],
        answered=True,
        answer_transcript="We used Redis for session caching.",
        evaluation=AnswerEvaluationResult(
            scores=[
                DimensionScore(
                    dimension=dim,
                    score=7.0,
                    rationale="Solid.",
                )
                for dim in EvaluationDimension
            ],
            overall_score=7.0,
            strengths=["Clear"],
            improvements=["Tradeoffs"],
            evaluator_name="fake",
        ),
    )
    session = SessionContext(
        status=EngineStatus.IN_PROGRESS,
        phase=InterviewPhase.PROJECTS,
        interview_type=InterviewType.TECHNICAL,
        company_name="EPAM",
        target_role="SDE intern",
        phase_sequence=[
            InterviewPhase.INTRODUCTION,
            InterviewPhase.RESUME,
            InterviewPhase.PROJECTS,
            InterviewPhase.CS_FUNDAMENTALS,
            InterviewPhase.FINAL,
        ],
        questions_per_phase={
            InterviewPhase.INTRODUCTION: 1,
            InterviewPhase.RESUME: 1,
            InterviewPhase.PROJECTS: 1,
            InterviewPhase.CS_FUNDAMENTALS: 1,
            InterviewPhase.FINAL: 0,
        },
        questions=[question],
        awaiting_answer=False,
    )
    return session, question


async def test_follow_up_service_generates_probe_question() -> None:
    session, answered = _session_with_answered_project()
    service = FollowUpService(
        FakeClaimExtractor(),
        FakeFollowUpGenerator(),
        max_follow_ups_per_answer=1,
        max_follow_ups_per_interview=3,
        allowed_phases=parse_allowed_phases("resume,projects,cs_fundamentals,behavioral"),
    )

    decision = await service.decide(session=session, answered=answered, plan=_plan())

    assert decision.should_follow_up is True
    assert decision.follow_up is not None
    assert "Redis" in decision.follow_up.text
    assert decision.claims[0].text == "We used Redis."


async def test_follow_up_service_skips_introduction_phase() -> None:
    session, answered = _session_with_answered_project()
    answered = answered.model_copy(update={"phase": InterviewPhase.INTRODUCTION})
    session = session.model_copy(
        update={"phase": InterviewPhase.INTRODUCTION, "questions": [answered]}
    )
    service = FollowUpService(
        FakeClaimExtractor(),
        FakeFollowUpGenerator(),
        max_follow_ups_per_answer=1,
        max_follow_ups_per_interview=3,
        allowed_phases=parse_allowed_phases("resume,projects"),
    )

    decision = await service.decide(session=session, answered=answered, plan=_plan())

    assert decision.should_follow_up is False
    assert "disabled for phase" in decision.reason


async def test_follow_up_service_respects_max_depth() -> None:
    session, answered = _session_with_answered_project()
    root_id = answered.id
    assert root_id is not None
    follow_up = SessionQuestion(
        id=uuid4(),
        position=1,
        phase=InterviewPhase.PROJECTS,
        text="Why Redis instead of Memcached?",
        category="project",
        difficulty="medium",
        expected_topics=["caching"],
        evaluation_rubric=["depth"],
        answered=True,
        answer_transcript="Because of data structures.",
        is_follow_up=True,
        parent_question_id=root_id,
        follow_up_depth=1,
    )
    session = session.model_copy(update={"questions": [answered, follow_up]})
    service = FollowUpService(
        FakeClaimExtractor(),
        FakeFollowUpGenerator(),
        max_follow_ups_per_answer=1,
        max_follow_ups_per_interview=3,
        allowed_phases=parse_allowed_phases("projects"),
    )

    decision = await service.decide(session=session, answered=follow_up, plan=_plan())

    assert decision.should_follow_up is False
    assert "Max follow-up depth" in decision.reason
