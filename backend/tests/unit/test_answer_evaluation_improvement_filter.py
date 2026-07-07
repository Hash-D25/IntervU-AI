"""Improvement contradiction filter tests."""

from app.features.evaluation.improvement_filter import filter_contradictory_improvements


def test_filters_quantify_leetcode_when_answer_already_has_count() -> None:
    answer = (
        "I actively practice competitive programming and have solved 800+ problems "
        "on platforms like LeetCode and Codeforces."
    )
    improvements = [
        "Quantify your claims, such as the number of problems solved on LeetCode.",
        "Explain your problem-solving approach for hard DP problems.",
    ]

    filtered = filter_contradictory_improvements(improvements, answer)

    assert len(filtered) == 1
    assert "problem-solving approach" in filtered[0]


def test_filters_mention_projects_when_answer_names_projects() -> None:
    answer = "I built UncDoIt and ytNotes as personal projects."
    improvements = [
        "Mention specific projects from your resume.",
        "Describe the architecture tradeoffs in UncDoIt.",
    ]

    filtered = filter_contradictory_improvements(improvements, answer)

    assert filtered == ["Describe the architecture tradeoffs in UncDoIt."]


def test_keeps_valid_improvements() -> None:
    answer = "I enjoy backend development."
    improvements = ["Add concrete metrics for API latency improvements."]

    assert filter_contradictory_improvements(improvements, answer) == improvements


def test_filters_cp_context_when_answer_already_covers_cp() -> None:
    answer = (
        "I actively practice competitive programming and have solved 800+ problems "
        "on platforms like LeetCode and Codeforces."
    )
    improvements = [
        "Provide more context about how your competitive programming experience "
        "has helped you develop strong analytical thinking.",
    ]

    assert filter_contradictory_improvements(improvements, answer) == []


def test_filters_auth_detail_request_when_auth_already_explained() -> None:
    answer = "I owned the auth module end-to-end with JWT refresh flow and Prisma schema."
    improvements = [
        "Offer more detailed explanations of authentication implementation specifics.",
    ]

    assert filter_contradictory_improvements(improvements, answer) == []
