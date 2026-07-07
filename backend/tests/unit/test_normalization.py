"""Normalization unit tests."""

from app.features.resume.parsing.normalization import normalize_string_list


def test_normalize_deduplicates_achievement_bullet_variants() -> None:
    values = [
        "∗Won amongst 125+ teams : Cursor Kashmir Hackathon 2026",
        "∗ Won amongst 125+ teams : Cursor Kashmir Hackathon 2026",
        "* Won amongst 125+ teams : Cursor Kashmir Hackathon 2026",
    ]
    assert len(normalize_string_list(values)) == 1


def test_normalize_deduplicates_near_duplicate_achievements() -> None:
    values = [
        "Solved more than 800 DSA questions on Codeforces, LeetCode, and HackerRank.",
        "Solved more than 800 DSA questions on Code forces, LeetCode, and HackerRank.",
    ]
    from app.features.resume.parsing.normalization import normalize_achievements

    assert len(normalize_achievements(values)) == 1


def test_normalize_splits_labeled_skill_line() -> None:
    values = ["Languages: Java, C, C++, JavaScript"]
    normalized = normalize_string_list(values)
    assert "Java" in normalized
    assert "C++" in normalized
    assert "JavaScript" in normalized


def test_normalize_keeps_commas_inside_parentheses() -> None:
    values = ["Other Skills: Problem Solving (800+ problems solved across Codeforces, LeetCode)"]
    normalized = normalize_string_list(values)
    assert len(normalized) == 1
    assert "Codeforces, LeetCode" in normalized[0]


def test_validator_collects_project_technologies() -> None:
    from app.features.resume.parsing.schemas import ParsedResume, ProjectEntry
    from app.features.resume.parsing.validator import ParsedResumeValidator

    parsed = ParsedResume(
        skills=["Python"],
        projects=[ProjectEntry(name="App", technologies=["TailwindCSS", "Vite", "Python"])],
    )
    validated = ParsedResumeValidator.validate(parsed)
    assert "TailwindCSS" in validated.technologies
    assert "Python" not in validated.technologies
