"""Follow-up decision policy and orchestration."""

from uuid import UUID

from app.features.interview.execution.schemas import InterviewPhase, SessionContext, SessionQuestion
from app.features.interview.follow_up.protocols import ClaimExtractor, FollowUpGenerator
from app.features.interview.follow_up.schemas import FollowUpContext, FollowUpDecision
from app.features.interview.planning.schemas import InterviewPlan

_DEFAULT_ALLOWED_PHASES = frozenset(
    {
        InterviewPhase.RESUME,
        InterviewPhase.PROJECTS,
        InterviewPhase.CS_FUNDAMENTALS,
        InterviewPhase.BEHAVIORAL,
    }
)


class FollowUpService:
    def __init__(
        self,
        claim_extractor: ClaimExtractor,
        generator: FollowUpGenerator,
        *,
        max_follow_ups_per_answer: int,
        max_follow_ups_per_interview: int,
        allowed_phases: frozenset[InterviewPhase],
    ) -> None:
        self._claim_extractor = claim_extractor
        self._generator = generator
        self._max_per_answer = max_follow_ups_per_answer
        self._max_per_interview = max_follow_ups_per_interview
        self._allowed_phases = allowed_phases

    async def decide(
        self,
        *,
        session: SessionContext,
        answered: SessionQuestion,
        plan: InterviewPlan,
    ) -> FollowUpDecision:
        if self._generator.name == "none":
            return FollowUpDecision(
                should_follow_up=False,
                reason="Follow-up generation is disabled",
            )
        if answered.phase not in self._allowed_phases:
            return FollowUpDecision(
                should_follow_up=False,
                reason=f"Follow-ups disabled for phase {answered.phase.value}",
            )
        if not answered.answer_transcript:
            return FollowUpDecision(
                should_follow_up=False,
                reason="Answer transcript is empty",
            )

        root_id = answered.parent_question_id or answered.id
        current_depth = root_follow_up_depth(session, root_id)
        if current_depth >= self._max_per_answer:
            return FollowUpDecision(
                should_follow_up=False,
                reason="Max follow-up depth reached for this answer",
            )

        interview_follow_ups = sum(1 for question in session.questions if question.is_follow_up)
        if interview_follow_ups >= self._max_per_interview:
            return FollowUpDecision(
                should_follow_up=False,
                reason="Max follow-ups for this interview reached",
            )

        previous = [
            question.text
            for question in session.questions
            if question.is_follow_up
            and (question.parent_question_id == root_id or question.id == root_id)
        ]
        context = FollowUpContext(
            company_name=session.company_name,
            target_role=session.target_role,
            phase=answered.phase,
            category=answered.category,
            question_text=answered.text,
            answer_transcript=answered.answer_transcript,
            evaluation=answered.evaluation,
            follow_up_strategy=plan.follow_up_strategy,
            focus_areas=plan.focus_areas,
            previous_follow_ups=previous,
            current_depth=current_depth,
            max_depth=self._max_per_answer,
            interview_follow_ups_used=interview_follow_ups,
            max_interview_follow_ups=self._max_per_interview,
        )

        claims = await self._claim_extractor.extract(context)
        if not claims:
            return FollowUpDecision(
                should_follow_up=False,
                reason="No probe-worthy claims found",
                claims=[],
            )

        follow_up = await self._generator.generate(context, claims=claims)
        if follow_up is None:
            return FollowUpDecision(
                should_follow_up=False,
                reason="Generator declined to create a follow-up",
                claims=claims,
            )

        return FollowUpDecision(
            should_follow_up=True,
            reason="Probe-worthy claim identified",
            claims=claims,
            follow_up=follow_up,
        )


def root_follow_up_depth(session: SessionContext, root_id: UUID | None) -> int:
    if root_id is None:
        return 0
    depths = [
        question.follow_up_depth
        for question in session.questions
        if question.is_follow_up and question.parent_question_id == root_id
    ]
    return max(depths, default=0)


def parse_allowed_phases(raw: str) -> frozenset[InterviewPhase]:
    phases: set[InterviewPhase] = set()
    for part in raw.split(","):
        key = part.strip().lower()
        if not key:
            continue
        try:
            phases.add(InterviewPhase(key))
        except ValueError:
            continue
    return frozenset(phases) if phases else _DEFAULT_ALLOWED_PHASES
