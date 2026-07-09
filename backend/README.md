# InterviewerAI - Backend

FastAPI service built with **Clean Architecture** and **feature-based** modules.

## Layering (per feature)

```
router  →  service  →  repository  →  db
   │          │            │
 (validate) (business)  (data access)
        DTOs cross boundaries; ORM models stay inside repositories.
```

Rules enforced by this structure:

- API routes only validate input and call services - never touch the DB.
- All business logic lives in services.
- Repositories isolate persistence; ORM models never leak past them.
- AI prompts live in `app/ai/prompts`, never inline in business logic.
- Configuration is read from environment variables via `app/core/config`.

## Folder map

```
app/
├── core/         # config, logging, exceptions, DI wiring
├── db/           # engine, session, declarative base
├── api/          # router aggregation + shared route dependencies
├── shared/       # framework-agnostic types & utilities
├── features/     # one folder per business capability
│   ├── resume/
│   ├── interview/
│   ├── evaluation/
│   └── feedback/
└── ai/           # AI boundary (kept swappable)
    ├── providers/       # LLMProvider interface + implementations
    ├── prompts/         # prompt templates as data
    ├── graphs/          # LangGraph interview state machines
    ├── vectorstore/     # ChromaDB wrapper
    └── transcription/   # Whisper wrapper
tests/
├── unit/
└── integration/
```

Each `features/*` module owns: `router`, `service`, `repository`, `models`,
`dto`, and its own tests.

## Setup

```bash
# From backend/ - create a virtual env (Python 3.13)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install base + dev deps. Add AI/voice groups as iterations require them.
pip install -e ".[dev]"
# pip install -e ".[dev,ai]"
# pip install -e ".[dev,ai,voice]"

cp .env.example .env
```

## Common commands

```bash
ruff check . && ruff format --check .   # lint + format
mypy app                                # type-check
pytest                                  # tests
alembic upgrade head                    # apply migrations
uvicorn app.main:app --reload           # run dev server (added in a later iteration)
```
