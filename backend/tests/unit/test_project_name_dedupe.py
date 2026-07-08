"""Project name normalization tests for duplicated titles."""

from app.features.resume.parsing.project_names import normalize_project_references_in_text


def test_dedupes_repeated_project_title_with_in() -> None:
    names = ["GitHub Repository Browser : Private Repo Viewer"]
    text = (
        "Can you walk us through how you implemented the "
        "GitHub Repository Browser : Private Repo Viewer in "
        "GitHub Repository Browser : Private Repo Viewer, focusing on tradeoffs?"
    )
    cleaned = normalize_project_references_in_text(text, names)
    assert cleaned.count("GitHub Repository Browser : Private Repo Viewer") == 1
