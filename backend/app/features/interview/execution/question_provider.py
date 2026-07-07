"""Generate questions for interview execution phases."""

from app.features.interview.execution.schemas import InterviewPhase, SessionQuestion
from app.features.interview.question_generation.protocols import QuestionGeneratorStrategy
from app.features.interview.question_generation.schemas import (
    GeneratedQuestion,
    QuestionCategory,
    QuestionGenerationContext,
)

_PHASE_CATEGORY: dict[InterviewPhase, QuestionCategory] = {
    InterviewPhase.INTRODUCTION: QuestionCategory.BEHAVIORAL,
    InterviewPhase.RESUME: QuestionCategory.PROJECT,
    InterviewPhase.PROJECTS: QuestionCategory.PROJECT,
    InterviewPhase.CS_FUNDAMENTALS: QuestionCategory.CS_FUNDAMENTALS,
    InterviewPhase.BEHAVIORAL: QuestionCategory.BEHAVIORAL,
}


def build_intro_question(
    *,
    company_name: str,
    target_role: str,
    position: int,
) -> SessionQuestion:
    return SessionQuestion(
        position=position,
        phase=InterviewPhase.INTRODUCTION,
        text=(
            f"Welcome! This interview will cover your background, projects, and technical "
            f"fundamentals for the {target_role} role at {company_name}. "
            f"To start, tell me about yourself and why you are interested in this opportunity."
        ),
        category=QuestionCategory.BEHAVIORAL.value,
        difficulty="easy",
        expected_topics=["background", "motivation", "role fit"],
        evaluation_rubric=["clarity", "relevance", "communication"],
    )


def generated_to_session_question(
    generated: GeneratedQuestion,
    *,
    phase: InterviewPhase,
    position: int,
) -> SessionQuestion:
    return SessionQuestion(
        position=position,
        phase=phase,
        text=generated.text,
        category=generated.category.value,
        difficulty=generated.difficulty.value,
        expected_topics=generated.expected_topics,
        evaluation_rubric=generated.evaluation_rubric,
    )


class PhaseQuestionProvider:
    def __init__(self, strategies: dict[QuestionCategory, QuestionGeneratorStrategy]) -> None:
        self._strategies = strategies

    async def generate_for_phase(
        self,
        phase: InterviewPhase,
        *,
        company_name: str,
        target_role: str,
        position: int,
        generation_context: QuestionGenerationContext,
    ) -> SessionQuestion:
        if phase == InterviewPhase.INTRODUCTION:
            return build_intro_question(
                company_name=company_name,
                target_role=target_role,
                position=position,
            )
        if phase == InterviewPhase.FINAL:
            raise ValueError("Final phase does not generate questions")

        category = _PHASE_CATEGORY[phase]
        strategy = self._strategies[category]
        generated = await strategy.generate(generation_context)
        return generated_to_session_question(generated, phase=phase, position=position)
