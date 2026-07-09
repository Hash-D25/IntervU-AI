# features/interview

Interview session lifecycle and dynamic question flow.

Responsibility: manage a session as an **explicit state machine** (not raw chat
history), driving contextual questions and adaptive follow-ups based on the
candidate's answers, parsed resume, and optional target job description.

This feature creates interview sessions, stores metadata and an interview plan,
generates questions by category, and runs a phase-based execution engine.

- `planning/` - session blueprint and legacy planning state snapshot
- `question_generation/` - category-specific LLM strategies (DSA, project, behavioral, CS)
- `execution/` - explicit phase engine (`INTRODUCTION` … `FINAL`), session context, API
