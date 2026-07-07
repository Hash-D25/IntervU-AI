"""Project name extraction and alignment tests."""

from app.features.resume.parsing.project_names import (
    align_project_names,
    align_question_text,
    extract_project_names,
    sanitize_project_name,
)
from app.features.resume.parsing.schemas import ProjectEntry

SAMPLE_PROJECTS_SECTION = """
PROJECTS
UncDoIt - AI Web Navigation Assistant Link
Built an AI-powered browser assistant that converts natural language instructions
into executable web actions.
Python, FastAPI, JavaScript, Chrome Extension MV3

ytNotes : YouTube Notes Chrome Extension
Built a Chrome extension for capturing timestamped YouTube notes and screenshots.
React, Node.js, MongoDB

GitHub Repository Browser : Private Repo Viewer
Built a GitHub repository explorer supporting private and public repositories.

Social Media App
Built a social media platform with JWT authentication and media uploads.
"""


def test_extract_project_names_from_section() -> None:
    projects = extract_project_names(SAMPLE_PROJECTS_SECTION)
    names = [project.name for project in projects]
    assert "UncDoIt - AI Web Navigation Assistant" in names
    assert any("ytNotes" in name for name in names)


def test_align_project_names_prefers_exact_reference() -> None:
    reference = [ProjectEntry(name="UncDoIt - AI Web Navigation Assistant")]
    llm_projects = [
        ProjectEntry(
            name="AI Web Navigation Assistant",
            description="Built an AI-powered browser assistant.",
            technologies=["Python"],
        )
    ]
    aligned = align_project_names(reference, llm_projects)
    assert aligned[0].name == "UncDoIt - AI Web Navigation Assistant"
    assert aligned[0].description == "Built an AI-powered browser assistant."


def test_extract_project_names_skips_technology_lines() -> None:
    projects = extract_project_names(SAMPLE_PROJECTS_SECTION)
    names = [project.name for project in projects]
    assert "Python, FastAPI, JavaScript, Chrome Extension MV3" not in names
    assert len(names) == 4


def test_extract_project_names_handles_colon_without_leading_space() -> None:
    text = """
PROJECTS
ytNotes: YouTube Notes Chrome Extension Link
Built a Chrome extension.
"""
    projects = extract_project_names(text)
    assert projects[0].name == "ytNotes: YouTube Notes Chrome Extension"


def test_align_project_names_normalizes_separator_spacing() -> None:
    reference = [ProjectEntry(name="ytNotes : YouTube Notes Chrome Extension")]
    llm_projects = [ProjectEntry(name="ytNotes: YouTube Notes Chrome Extension")]
    aligned = align_project_names(reference, llm_projects)
    assert aligned[0].name == "ytNotes : YouTube Notes Chrome Extension"


def test_sanitize_project_name_fixes_ocr_and_link_artifacts() -> None:
    assert (
        sanitize_project_name("UncDoIt - AI W eb Navigation AssistantLink")
        == "UncDoIt - AI Web Navigation Assistant"
    )
    assert (
        sanitize_project_name("ytNotes : Y ouT ube Notes Chrome ExtensionLive Extension")
        == "ytNotes : YouTube Notes Chrome Extension"
    )
    assert (
        sanitize_project_name("GitHub Repository Browser : Private Repo ViewerLive")
        == "GitHub Repository Browser : Private Repo Viewer"
    )
    assert sanitize_project_name("Social Media App Live") == "Social Media App"


def test_align_question_text_replaces_noisy_project_reference() -> None:
    names = [
        "UncDoIt - AI Web Navigation Assistant",
        "ytNotes : YouTube Notes Chrome Extension",
    ]
    text = (
        "Describe the architecture of using a stateful vs stateless approach for web "
        "navigation in UncDoIt - AI Web Navigation Assistant Link."
    )
    aligned = align_question_text(text, names)
    assert "UncDoIt - AI Web Navigation Assistant Link" not in aligned
    assert "UncDoIt - AI Web Navigation Assistant" in aligned


def test_align_question_text_preserves_unrelated_content() -> None:
    names = ["UncDoIt - AI Web Navigation Assistant"]
    text = "Explain REST API design patterns in FastAPI."
    assert align_question_text(text, names) == text


def test_normalize_project_references_fixes_dashes_and_quotes() -> None:
    from app.features.resume.parsing.project_names import normalize_project_references_in_text

    names = ["UncDoIt - AI Web Navigation Assistant"]
    text = (
        "Walk me through the system architecture of "
        "'UncDoIt – AI Web Navigation Assistant'."
    )
    normalized = normalize_project_references_in_text(text, names)
    assert "–" not in normalized
    assert "'UncDoIt" not in normalized
    assert "UncDoIt - AI Web Navigation Assistant" in normalized
