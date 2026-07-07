"""Question category selector tests."""

from app.features.interview.planning.schemas import InterviewPlan
from app.features.interview.question_generation.schemas import QuestionCategory
from app.features.interview.question_generation.selector import select_question_categories


def test_select_question_categories_maps_mix_items() -> None:
    plan = InterviewPlan(
        focus_areas=["Python"],
        question_mix=[
            "resume_deep_dive",
            "technical_core",
            "project_walkthrough",
            "job_alignment",
        ],
        estimated_rounds=2,
        follow_up_strategy="Deepen on weak answers.",
        evaluation_axes=["clarity"],
    )

    categories = select_question_categories(plan)

    assert categories == [
        QuestionCategory.PROJECT,
        QuestionCategory.DSA,
        QuestionCategory.PROJECT,
        QuestionCategory.CS_FUNDAMENTALS,
    ]


def test_select_question_categories_alternates_technical_core() -> None:
    plan = InterviewPlan(
        focus_areas=["Java"],
        question_mix=["technical_core", "technical_core"],
        estimated_rounds=1,
        follow_up_strategy="Probe deeper.",
        evaluation_axes=["depth"],
    )

    categories = select_question_categories(plan)

    assert categories == [QuestionCategory.DSA, QuestionCategory.CS_FUNDAMENTALS]
