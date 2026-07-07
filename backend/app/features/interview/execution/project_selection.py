"""Select projects and phase instructions for diverse interview questions."""

from app.features.interview.execution.schemas import InterviewPhase, SessionContext, SessionQuestion
from app.features.resume.parsing.project_names import (
    name_match_key,
    project_marker,
    sanitize_project_name,
)


def build_execution_hints(
    *,
    session: SessionContext,
    project_names: list[str],
    experience_titles: list[str],
) -> dict[str, object]:
    phase = session.phase
    if phase is None or phase in {InterviewPhase.INTRODUCTION, InterviewPhase.FINAL}:
        return {}

    canonical = [sanitize_project_name(name) for name in project_names if name.strip()]
    covered = projects_covered_in_questions(session.questions, canonical)
    previous_topics = _previous_topics(session.questions)

    hints: dict[str, object] = {
        "execution_phase": phase,
        "projects_already_covered": covered,
        "previous_question_topics": previous_topics,
    }

    if phase == InterviewPhase.RESUME:
        comparison = _pick_comparison_projects(canonical, covered)
        hints["comparison_project_names"] = comparison
        hints["focus_project_names"] = comparison[:1]
        hints["phase_instruction"] = _resume_phase_instruction(
            comparison_projects=comparison,
            experience_titles=experience_titles,
        )
    elif phase == InterviewPhase.PROJECTS:
        focus = _pick_unused_project(canonical, covered)
        hints["focus_project_names"] = [focus] if focus else []
        hints["phase_instruction"] = _projects_phase_instruction(
            focus_project=focus,
            covered_projects=covered,
        )
    elif phase == InterviewPhase.CS_FUNDAMENTALS:
        hints["phase_instruction"] = _cs_phase_instruction(previous_topics=previous_topics)
    elif phase == InterviewPhase.BEHAVIORAL:
        hints["phase_instruction"] = _behavioral_phase_instruction(
            experience_titles=experience_titles,
            previous_topics=previous_topics,
        )

    return hints


def projects_covered_in_questions(
    questions: list[SessionQuestion],
    project_names: list[str],
) -> list[str]:
    covered: list[str] = []
    for name in project_names:
        marker = project_marker(name)
        name_key = name_match_key(name)
        for question in questions:
            text_key = name_match_key(question.text)
            if name_key in text_key or marker.lower() in question.text.lower():
                covered.append(name)
                break
    return covered


def _pick_comparison_projects(
    project_names: list[str],
    covered: list[str],
) -> list[str]:
    unused = [name for name in project_names if name not in covered]
    pool = unused if len(unused) >= 2 else project_names
    if len(pool) >= 2:
        return pool[:2]
    return pool[:1]


def _pick_unused_project(project_names: list[str], covered: list[str]) -> str | None:
    for name in project_names:
        if name not in covered:
            return name
    return project_names[-1] if project_names else None


def _previous_topics(questions: list[SessionQuestion]) -> list[str]:
    topics: list[str] = []
    seen: set[str] = set()
    for question in questions:
        for topic in question.expected_topics:
            key = topic.casefold()
            if key in seen:
                continue
            seen.add(key)
            topics.append(topic)
    return topics


def _resume_phase_instruction(
    *,
    comparison_projects: list[str],
    experience_titles: list[str],
) -> str:
    if len(comparison_projects) >= 2:
        return (
            "RESUME phase: Ask one breadth question comparing "
            f"'{comparison_projects[0]}' and '{comparison_projects[1]}'. "
            "Focus on differences in purpose, architecture, or tech choices. "
            "Do NOT deep-dive implementation details — save those for the projects phase."
        )
    if comparison_projects:
        project = comparison_projects[0]
        experience = experience_titles[0] if experience_titles else "internship experience"
        return (
            f"RESUME phase: Connect '{project}' to the candidate's {experience}. "
            "Ask a holistic resume question, not a deep implementation walkthrough."
        )
    return (
        "RESUME phase: Ask a breadth question about the candidate's background and experience."
    )


def _projects_phase_instruction(*, focus_project: str | None, covered_projects: list[str]) -> str:
    if focus_project:
        covered = ", ".join(covered_projects) if covered_projects else "none"
        return (
            f"PROJECTS phase: Deep-dive ONLY '{focus_project}'. "
            f"Ask about implementation, challenges, and tradeoffs. "
            f"Do NOT ask about projects already covered ({covered})."
        )
    return (
        "PROJECTS phase: Deep-dive one project with implementation and tradeoff focus."
    )


def _cs_phase_instruction(*, previous_topics: list[str]) -> str:
    avoided = ", ".join(previous_topics[:8]) if previous_topics else "none"
    return (
        "CS_FUNDAMENTALS phase: Ask one practical fundamentals question grounded in "
        "resume.primary_technologies and real project/internship experience. "
        f"Avoid repeating topics already covered ({avoided}). "
        "Prefer Python/FastAPI/PostgreSQL stack when present on the resume."
    )


def _behavioral_phase_instruction(
    *,
    experience_titles: list[str],
    previous_topics: list[str],
) -> str:
    role = experience_titles[0] if experience_titles else "recent experience"
    avoided = ", ".join(previous_topics[:6]) if previous_topics else "none"
    return (
        f"BEHAVIORAL phase: Ask one STAR-style question tied to {role}. "
        f"Avoid repeating themes already covered ({avoided})."
    )
