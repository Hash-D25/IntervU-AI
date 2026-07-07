"""Map interview plan mix items to question categories."""

from app.features.interview.planning.schemas import InterviewPlan
from app.features.interview.question_generation.schemas import QuestionCategory

_MIX_TO_CATEGORY: dict[str, QuestionCategory] = {
    "resume_deep_dive": QuestionCategory.PROJECT,
    "technical_core": QuestionCategory.DSA,
    "project_walkthrough": QuestionCategory.PROJECT,
    "behavioral": QuestionCategory.BEHAVIORAL,
    "collaboration": QuestionCategory.BEHAVIORAL,
    "job_alignment": QuestionCategory.CS_FUNDAMENTALS,
}


def select_question_categories(plan: InterviewPlan) -> list[QuestionCategory]:
    categories: list[QuestionCategory] = []
    technical_core_count = 0
    for mix_item in plan.question_mix:
        if mix_item == "technical_core":
            category = (
                QuestionCategory.DSA
                if technical_core_count % 2 == 0
                else QuestionCategory.CS_FUNDAMENTALS
            )
            technical_core_count += 1
        else:
            category = _MIX_TO_CATEGORY.get(mix_item, QuestionCategory.PROJECT)
        categories.append(category)

    if not categories:
        categories = [QuestionCategory.DSA, QuestionCategory.PROJECT]

    max_questions = max(plan.estimated_rounds * 2, len(categories))
    return categories[:max_questions]
