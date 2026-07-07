"""Rule-based pre-extraction from resume plain text."""

import json
import re

from app.features.resume.parsing.normalization import (
    dedupe_key,
    normalize_list_item,
    split_list_values,
)
from app.features.resume.parsing.project_names import extract_project_names
from app.features.resume.parsing.schemas import ParsedResume

_SKILLS_SECTION = re.compile(
    r"(?im)^(?:skills|technical skills|core competencies|key skills)\s*[:\-]?\s*(.+)$"
)
_TECH_SECTION = re.compile(
    r"(?im)^(?:technologies|tech stack|tools|technical tools)\s*[:\-]?\s*(.+)$"
)
_LABELED_SKILL_LINE = re.compile(
    r"^(?:languages?|frameworks?(?:/libraries)?|database|tools?|concepts?|"
    r"java technologies|other skills?)\s*:\s*(.+)$",
    re.IGNORECASE,
)
_LIST_SPLIT = re.compile(r"[,|•·\u2022;/]+")
_ACHIEVEMENT_HEADER = re.compile(
    r"(?im)^(?:achievements|awards|honors|accomplishments|key achievements|"
    r"certifications(?:\s*&\s*awards)?)\s*:?\s*$"
)
_BULLET_LINE = re.compile(r"^[\-*•·∗]\s*(.+)$")
_ANY_SECTION_HEADER = re.compile(
    r"^(?:experience|work experience|employment|education|projects|skills|"
    r"achievements|awards|honors|summary|objective|certifications|technologies)\b",
    re.IGNORECASE,
)

_KEYWORDS = frozenset(
    {
        "python",
        "javascript",
        "typescript",
        "java",
        "c++",
        "c#",
        "go",
        "rust",
        "kotlin",
        "swift",
        "ruby",
        "php",
        "sql",
        "html",
        "css",
        "react",
        "next.js",
        "nextjs",
        "vue",
        "angular",
        "node.js",
        "nodejs",
        "fastapi",
        "django",
        "flask",
        "spring",
        "express",
        "postgresql",
        "postgres",
        "mysql",
        "mongodb",
        "redis",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "gcp",
        "git",
        "linux",
        "tensorflow",
        "pytorch",
        "pandas",
        "numpy",
        "scikit-learn",
        "machine learning",
        "deep learning",
        "nlp",
        "langchain",
        "langgraph",
        "openai",
        "rest",
        "graphql",
        "microservices",
        "ci/cd",
        "terraform",
        "ansible",
        "kafka",
        "rabbitmq",
        "elasticsearch",
        "spark",
        "hadoop",
        "tableau",
        "power bi",
        "figma",
        "jira",
        "agile",
        "scrum",
    }
)


class RuleBasedResumeExtractor:
    """Extract skills and technologies cheaply before calling an LLM."""

    def extract(self, text: str) -> ParsedResume:
        skills = self._merge_strings(
            self._extract_section_items(text, _SKILLS_SECTION),
            self._extract_labeled_skill_lines(text),
            self._scan_keywords(text),
        )
        technologies = self._merge_strings(
            self._extract_section_items(text, _TECH_SECTION),
        )
        achievements = self._extract_achievements_section(text)
        projects = extract_project_names(text)
        return ParsedResume(
            skills=skills,
            technologies=technologies,
            achievements=achievements,
            projects=projects,
        )

    @staticmethod
    def needs_llm(partial: ParsedResume) -> bool:
        return not (partial.projects and partial.experience and partial.education)

    @staticmethod
    def to_prompt_json(partial: ParsedResume) -> str:
        return json.dumps(
            {
                "skills": partial.skills,
                "projects": [project.model_dump() for project in partial.projects],
                "experience": [entry.model_dump() for entry in partial.experience],
                "technologies": partial.technologies,
                "education": [entry.model_dump() for entry in partial.education],
                "achievements": [],
            },
            separators=(",", ":"),
        )

    @classmethod
    def _extract_achievements_section(cls, text: str) -> list[str]:
        lines = text.splitlines()
        items: list[str] = []
        in_section = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if _ACHIEVEMENT_HEADER.match(stripped):
                in_section = True
                inline = stripped.split(":", 1)
                if len(inline) == 2 and inline[1].strip():
                    items.extend(cls._split_list(inline[1]))
                continue
            if in_section and _ANY_SECTION_HEADER.match(stripped):
                break
            if not in_section:
                continue
            bullet = _BULLET_LINE.match(stripped)
            raw = bullet.group(1).strip() if bullet else stripped
            items.append(normalize_list_item(raw))

        return cls._merge_strings(items)

    @classmethod
    def _extract_labeled_skill_lines(cls, text: str) -> list[str]:
        items: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            match = _LABELED_SKILL_LINE.match(stripped)
            if match is None:
                continue
            items.extend(cls._split_list(match.group(1)))
        return items

    @classmethod
    def _extract_section_items(cls, text: str, pattern: re.Pattern[str]) -> list[str]:
        match = pattern.search(text)
        if match is None:
            return []
        return cls._split_list(match.group(1))

    @classmethod
    def _split_list(cls, raw: str) -> list[str]:
        return [item.strip() for item in split_list_values(raw) if item.strip()]

    @classmethod
    def _scan_keywords(cls, text: str) -> list[str]:
        lowered = text.casefold()
        found: list[str] = []
        for keyword in sorted(_KEYWORDS, key=len, reverse=True):
            found_keys = {dedupe_key(item) for item in found}
            if keyword in lowered and dedupe_key(keyword) not in found_keys:
                found.append(keyword)
        return found

    @staticmethod
    def _merge_strings(*groups: list[str]) -> list[str]:
        seen: set[str] = set()
        merged: list[str] = []
        for group in groups:
            for value in group:
                cleaned = normalize_list_item(value)
                if not cleaned:
                    continue
                key = dedupe_key(cleaned)
                if key in seen:
                    continue
                seen.add(key)
                merged.append(cleaned)
        return merged
