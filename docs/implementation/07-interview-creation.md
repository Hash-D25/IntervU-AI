# 07 — Interview Creation

## Goal

Create an interview session from a **parsed resume**, company, target role, and
interview type. Store interview metadata, initial session state, and an
interview plan. **Do not generate questions yet.**

## Scope

**In:** extended `Interview` model, state machine schemas, `InterviewPlanner`
protocol, `ResumeBasedInterviewPlanner`, `InterviewService`, create/get routes,
migration `0006_interview_creation_state`, project name sanitization for clean
metadata, tests.

**Out:** question generation, answer capture, state transitions during live
interview (Iteration 08+).

---

## Architecture

```
POST /api/v1/interviews/
        │
        ▼
InterviewService.create()
        │
        ├── ResumeRepository.get_for_user()
        ├── ResumeParsedProfileRepository (must be completed)
        ├── InterviewPlanner.build_plan()
        └── InterviewRepository.add() + commit
```

### Planning layer

```
ResumeBasedInterviewPlanner
        │
        ├── reads ParsedResume
        ├── optional job_description text
        └── produces InterviewBlueprint
                ├── metadata (company, role, resume summary, context sources)
                ├── session_state snapshot (ready + allowed transitions)
                └── interview_plan (focus areas, question mix, rubric axes)
```

### State machine (foundation for future flow)

| Session state | Meaning |
| ------------- | ------- |
| `draft` | Not yet ready |
| `ready` | Session created, no questions asked |
| `asking_intro` / `asking_core` / `asking_follow_up` | Question phases |
| `awaiting_answer` / `evaluating_answer` | Answer loop |
| `finished` | Interview complete |

Lifecycle `status` on the row remains separate: `created` → `in_progress` →
`completed` / `abandoned`.

| Piece | Location |
| ----- | -------- |
| ORM extensions | `features/interview/models.py` |
| Planning schemas | `features/interview/planning/schemas.py` |
| State machine rules | `features/interview/planning/state_machine.py` |
| Planner protocol | `features/interview/planning/protocols.py` |
| Default planner | `planning/strategies/resume_based_planner.py` |
| Service | `features/interview/service.py` |
| Router | `features/interview/router.py` |
| Migration | `migrations/versions/0006_interview_creation_state.py` |

---

## New `interviews` columns

| Column | Type | Purpose |
| ------ | ---- | ------- |
| `resume_id` | FK → `resumes.id` | Link to uploaded resume |
| `interview_type` | enum | `technical` / `behavioral` / `mixed` |
| `session_state` | enum | Current state-machine position |
| `interview_metadata` | JSONB | Company, role, resume summary, context sources |
| `interview_plan` | JSONB | Focus areas, question mix, evaluation axes |

`job_description` (text column from Iteration 01) stores optional raw JD text
passed at creation time.

---

## API

| Method | Path | Description |
| ------ | ---- | ----------- |
| POST | `/api/v1/interviews/` | Create session (requires parsed resume) |
| GET | `/api/v1/interviews/{id}` | Fetch session |

### Request body

```json
{
  "resume_id": "uuid",
  "company_name": "EPAM",
  "target_role": "AI-Native Software Engineering Intern",
  "interview_type": "technical",
  "job_description": "optional raw JD text"
}
```

When `job_description` is provided, `context_sources` includes both
`parsed_resume` and `job_description`, and the plan adds `job_alignment` to the
question mix.

---

## Prerequisites

1. Resume uploaded and **parsed** (`parse_status: completed`).
2. Alembic migration applied:

```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

Without migration `0006`, inserts fail with `column "resume_id" does not exist`.

---

## Project name cleanup

Parsed PDF text can produce noisy project titles (`AssistantLink`, `W eb`).
`sanitize_project_name()` in `resume/parsing/project_names.py` cleans names at
parse time and in the interview planner's `resume_summary`.

---

## Verification

```bash
ruff check . && mypy app
pytest tests/unit/test_interview_planner.py tests/integration/test_interview_creation.py -q
```

---

## How to try it

1. Upload + parse resume.
2. Optionally analyze a JD (Iteration 06) and paste text into `job_description`.
3. `POST /interviews/` with your `resume_id`.
4. Confirm `session_state.current` is `ready` and `interview_plan` is populated.

## What's next

Iteration 08 — question generation from interview plan + resume + JD context.
