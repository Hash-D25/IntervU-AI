"""Project name extraction and alignment tests."""

from app.features.resume.parsing.project_names import align_project_names, extract_project_names
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
