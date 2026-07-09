# 00 - Project Setup

## Goal

Create a clean, empty-but-organized monorepo with all tooling, dependency
manifests, and folder structure in place - **no application code**.

## Scope

**In:** repo layout, git init, dependency manifests, linters/formatters/type
checkers, docker infra, per-module documentation, dependency installation.

**Out:** any runtime code, config-loading logic, database wiring (that is
Iteration 01).

---

## What we decided and why

### Monorepo (backend + frontend + shared infra)

We keep both apps in one repository with a root `docker-compose.yml` for local
infra (PostgreSQL + ChromaDB).

- **Why:** single-team project, atomic cross-cutting changes, one place to clone
  and run. Easy to split into separate repos later if needed.
- **Alternative considered:** two repos. Rejected - adds coordination overhead
  with no benefit at this stage.

### Feature-based, not layer-based, organization

Backend is organized as `features/<capability>/{router,service,repository,...}`
rather than global `controllers/`, `services/`, `models/` folders.

- **Why:** everything about one capability lives together (high cohesion); the
  architecture rules (thin routes, logic in services, DB in repositories) are
  enforced by physical structure.
- **Alternative:** layer-based monolith. Rejected - scatters a single feature
  across many top-level folders and grows into a "big ball of mud".

### The AI boundary is isolated up front

Everything model-specific lives under `app/ai/` (`providers`, `prompts`,
`graphs`, `vectorstore`, `transcription`).

- **Why:** the product must keep providers replaceable and never couple business
  logic to a vendor SDK. Prompts are stored as data, separate from logic.

### Dependencies split into groups

`pyproject.toml` defines `dependencies` (core) plus optional groups: `ai`,
`voice`, `dev`.

- **Why:** the base install stays light. Heavy AI/voice libraries (ChromaDB,
  Whisper) are installed only in the iteration that needs them.

### Version pinning strategy

- **Backend:** lower bounds (`>=`) on well-known packages; the resolver picks
  concrete versions. Avoids inventing exact pins.
- **Frontend:** caret ranges (`^`) to real released majors.

---

## Folder structure created

```
IntervU AI/
├── .gitignore · .editorconfig · .env.example · docker-compose.yml · README.md
├── backend/
│   ├── pyproject.toml          # deps + ruff/mypy(strict)/pytest/coverage config
│   ├── .env.example · README.md
│   └── app/
│       ├── core/  db/  api/  shared/         # infra & wiring (docs only at setup)
│       ├── features/ resume · interview · evaluation · feedback
│       └── ai/ providers · prompts · graphs · vectorstore · transcription
│   └── tests/ unit · integration
└── frontend/
    ├── package.json · tsconfig.json · next.config.mjs
    ├── tailwind.config.ts · postcss.config.mjs · .env.local.example · README.md
    └── src/ app · features · components · lib · stores · types
```

Every significant folder got a `README.md` describing its single
responsibility, so the structure is self-documenting.

---

## Tooling configuration (in `backend/pyproject.toml`)

- **Ruff** - lint + format; rule set `E, F, I, B, C4, UP, SIM`; line length 100.
- **mypy** - `strict = true`, pydantic plugin, Python 3.13.
- **pytest** - `asyncio_mode = "auto"`, `testpaths = ["tests"]`.
- **coverage** - branch coverage, source `app`.

Frontend: TypeScript `strict` + `noUncheckedIndexedAccess`, path alias `@/* ->
src/*`; Tailwind content globs cover `app`, `components`, `features`.

---

## Dependencies installed

**Backend (`.venv`, editable `.[dev]`):** fastapi 0.139, sqlalchemy 2.0.51,
alembic 1.18.5, pydantic 2.13 + pydantic-settings 2.14, psycopg 3.3 (binary),
uvicorn 0.50, structlog 26.1, httpx 0.28; dev: ruff 0.15, mypy 2.1, pytest 9.1
(+ asyncio, cov).

**Frontend (`node_modules`, 417 packages):** next 15, react 19, react-query 5,
zustand 5, tailwind 3.4, typescript 5.7.

**Not installed yet (deliberate):** `ai` and `voice` groups.

### Driver choice: psycopg 3 (not asyncpg)

`DATABASE_URL` uses `postgresql+psycopg://...`. psycopg 3 supports **both** async
(app) and sync (Alembic) with a single driver, avoiding a second dependency.

---

## Commands run

```bash
git init
python -m venv .venv && .venv\Scripts\python -m pip install -e ".[dev]"   # backend
npm install                                                                # frontend
```

## Notes & gotchas

- `.gitignore` initially ignored `frontend/.env.local.example` because the
  pattern `.env.*` swallowed it. Fixed by negating with `!*.example` so all
  template env files stay tracked.
- npm reported 2 moderate advisories on a fresh Next install - left as-is;
  `npm audit fix --force` can introduce breaking changes.
