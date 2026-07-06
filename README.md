# InterviewerAI

An AI-powered mock interview platform that simulates realistic technical and
behavioral interviews. It behaves like a real interviewer: it asks contextual,
resume- and job-description-aware questions, generates follow-ups, adapts to the
candidate's answers, evaluates responses, and produces actionable feedback.

> The goal is not a chatbot. The goal is an interviewer that acts as a **coach,
> not a judge**.

---

## Monorepo layout

```
IntervU AI/
├── backend/            # FastAPI service (Clean Architecture, feature-based)
├── frontend/           # Next.js app (App Router, feature-based)
├── docker-compose.yml  # Local infra: PostgreSQL + ChromaDB
└── README.md
```

Each app has its own README with setup instructions:

- [`backend/README.md`](./backend/README.md)
- [`frontend/README.md`](./frontend/README.md)

---

## Core features

| Feature                    | Description                                                        |
| -------------------------- | ------------------------------------------------------------------ |
| Resume-aware interviews    | Extract skills/projects/tech/experience; personalize questions.    |
| Job-description-aware      | Adapt questions to company, role, and JD.                          |
| Dynamic interviews         | Analyze answers, identify claims, probe deeper with follow-ups.    |
| Voice interviews           | Interviewer speaks; candidate replies by voice; auto-transcribed.  |
| Evaluation                 | Score accuracy, completeness, communication, examples, depth.      |
| Feedback reports           | Strengths, weaknesses, improvement suggestions, learning roadmap.  |

---

## Tech stack

**Backend:** Python 3.13 · FastAPI · PostgreSQL · SQLAlchemy 2 · Alembic · Pydantic v2
**Frontend:** Next.js · TypeScript · TailwindCSS · React Query · Zustand
**AI:** LangGraph · LangChain · ChromaDB · OpenAI-compatible models · Whisper

AI providers are kept behind abstractions so they can be swapped without touching
business logic.

---

## Architecture principles

- **Clean Architecture** with a **service layer** and **repository pattern**.
- **Thin controllers**, **focused services**, **isolated repositories**.
- **DTOs** cross layer boundaries; ORM models never leak out of repositories.
- **Explicit state machines** drive interview flow (never rely on chat history alone).
- Prompts live in a dedicated `prompts/` area, never inline in business logic.
- Configuration comes from environment variables.

See [`docs/`](./docs) for the living **implementation documentation** (one file
per iteration explaining what was built and why), and per-folder `README.md`
files that describe each module's single responsibility.

---

## Getting started (local dev)

Prerequisites: Docker, Python 3.13, Node.js 22+.

```bash
# 1. Start infra (PostgreSQL + ChromaDB)
docker compose up -d

# 2. Backend  (see backend/README.md)
cd backend

# 3. Frontend (see frontend/README.md)
cd frontend
```

Detailed, per-app steps live in each app's README. Feature code is added
iteration by iteration.
