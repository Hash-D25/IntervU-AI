# 02 - Database Layer

## Goal

Model the domain and give every entity a clean persistence path: SQLAlchemy 2
models with UUID keys and timestamps, a generic repository base plus concrete
repositories, the initial Alembic migration, and repository tests. **Database
code only** - no services, routes, or AI.

## Scope

**In:** `User`, `Interview`, `Question`, `Answer`, `FeedbackReport` models;
mixins; `BaseRepository`; concrete repos; model registry; initial migration;
SQLite repository tests; `aiosqlite` dev dep.

**Out:** services/business logic, API routes, validation DTOs, auth fields.

---

## Entity-relationship model

```
User ──1:N──> Interview ──1:N──> Question ──1:1──> Answer
                  │
                  └──1:1──> FeedbackReport
```

- Deleting an `Interview` cascades to its `Question`s, `Answer`s, and
  `FeedbackReport` (DB-level `ON DELETE CASCADE` + ORM `delete-orphan`).
- One `Answer` per `Question` and one `FeedbackReport` per `Interview` are
  enforced with **unique** foreign keys.

### Columns (beyond `id`, `created_at`, `updated_at`)

| Entity | Columns |
| ------ | ------- |
| User | `email` (unique index), `full_name` |
| Interview | `user_id` (FK), `role`, `company?`, `job_description?`, `status` (enum) |
| Question | `interview_id` (FK), `position`, `text`, `kind` (enum) |
| Answer | `question_id` (FK, unique), `transcript` |
| FeedbackReport | `interview_id` (FK, unique), `summary`, `strengths`/`weaknesses`/`suggestions`/`roadmap` (JSONB lists), `overall_score?` |

**Enums:** `InterviewStatus{created,in_progress,completed,abandoned}`,
`QuestionKind{technical,behavioral,follow_up}` - Python `StrEnum`, stored as
native Postgres enum types using the enum *values* (via `values_callable`).

---

## Decisions & tradeoffs

### Mixins (composition over inheritance)

`db/mixins.py` provides `UUIDPrimaryKeyMixin` and `TimestampMixin`. Models pick
what they need. SQLAlchemy copies mixin columns into each mapped class.

- UUID pk: `sa.Uuid` + `default=uuid4` (native `UUID` on Postgres, portable
  elsewhere).
- Timestamps: `DateTime(timezone=True)`, `created_at` server-default `now()`,
  `updated_at` server-default `now()` + `onupdate=now()`.

### Interview aggregate in one module

`Interview`, `Question`, `Answer` live together in
`features/interview/models.py` - they're one aggregate and share relationships.
Under 300 lines; split later only if needed.

### Generic repository (SOLID)

`db/repository.py` → `BaseRepository[ModelT: Base]` (PEP 695 generics) with
`get`, `list`, `add`, `delete`.

- **SRP** one entity per concrete repo · **OCP** extend via subclass ·
  **LSP** subclasses are drop-in · **ISP** base stays minimal, special queries
  in subclasses · **DIP** repos receive an `AsyncSession` (injected).
- **Transaction boundary:** repos `flush` (assign IDs / surface constraint
  errors) but **never `commit`** - commit belongs to the service/request layer
  (next iterations).
- **Why a generic class, not a `Protocol` + impl:** the class *is* the
  abstraction; a separate interface would add indirection with no current value.

Concrete repos: `UserRepository` (`get_by_email`), `InterviewRepository`
(`list_for_user`), `QuestionRepository` (`list_for_interview`),
`AnswerRepository` (`get_for_question`), `FeedbackReportRepository`
(`get_for_interview`).

### JSONB with a portable variant

Feedback list columns use `JSON().with_variant(JSONB, "postgresql")` →
**JSONB on Postgres**, plain JSON on SQLite (so unit tests run without Postgres).

- **Why JSON, not child tables:** these are display strings (strengths, etc.),
  not relationally queried; a table each would be over-engineering.

### Model registry

`db/registry.py` imports `Base` + every model so importing it registers the full
schema on `Base.metadata`. Used by Alembic `env.py` and tests - one import
instead of many, and no risk of a model being missed by autogenerate.

---

## Migration

`migrations/versions/0001_initial_schema.py` creates all five tables.

- **Why hand-written:** Docker/Postgres was unavailable here, so
  `--autogenerate` (which needs a live DB to diff) couldn't run. The schema is
  deterministic, so the migration was written directly against Postgres
  (native `ENUM` + `JSONB`) with constraint/index names matching the project
  naming convention.
- **Offline validation:** `alembic upgrade head --sql` (offline mode) executes
  the script and emits Postgres DDL **without a database connection**. Confirmed:
  `UUID` PKs, `TIMESTAMP WITH TIME ZONE DEFAULT now()`, `CREATE TYPE ... AS
  ENUM`, `JSONB` columns, and `FOREIGN KEY ... ON DELETE CASCADE`.
- **Applied live:** once Docker was available, the migration was applied to a
  running Postgres:

  ```bash
  docker compose up -d postgres
  cd backend && .venv\Scripts\alembic upgrade head   # -> 0001_initial_schema (head)
  ```

  Verified tables: `users, interviews, questions, answers, feedback_reports`
  (+ `alembic_version`).

### Alembic runs synchronously

`migrations/env.py` uses a **synchronous** engine (`create_engine`), even though
the app is async.

- **Why:** Alembic doesn't need async, and psycopg's async mode cannot use
  Windows' default `ProactorEventLoop` (it raises `InterfaceError`). A sync
  engine is simpler and fully cross-platform. (This replaced the initial async
  env after hitting that error on Windows.)

---

## Testing

`tests/unit/test_repositories.py` runs against **in-memory SQLite**
(`aiosqlite`), creating tables from `Base.metadata`. Coverage:

- User add / get / `get_by_email` (hit + miss).
- Interview→Question→Answer creation and relationship loading.
- One-to-one `Answer` lookup.
- `list_for_user`.
- FeedbackReport JSONB round-trip + score.
- Cascade delete removes children.

**Fidelity note:** SQLite validates repository *logic*, not Postgres specifics
(real JSONB, enum types, FK cascade at the DB level). A Postgres-backed
integration suite comes in a later iteration.

---

## Commands & verification

```bash
ruff check . && ruff format --check .   # All checks passed
mypy app                                # Success: no issues found in 34 source files
pytest -q                               # 6 passed (health + 5 repository tests)
alembic upgrade head --sql              # valid Postgres DDL generated offline
```

## Files

New: `db/mixins.py`, `db/repository.py`, `db/registry.py`,
`features/user/{__init__,models,repository}.py` (+ README),
`features/interview/{__init__,models,repository}.py`,
`features/feedback/{__init__,models,repository}.py`,
`features/__init__.py`, `migrations/versions/0001_initial_schema.py`,
`tests/unit/test_repositories.py`.
Changed: `migrations/env.py` (import registry), `pyproject.toml` (`aiosqlite`).

## Notes & gotchas

- `Column(unique=True, index=True)` yields a **single unique index** (e.g.
  `ix_users_email`), not a separate unique constraint - reflected in the
  migration.
- Async ORM has no lazy loading; tests use `session.refresh(obj, ["questions"])`
  to load relationships explicitly.
- Repos don't commit; tests rely on `flush` + identity map, which is sufficient
  to read back within the same session.
- **`DATABASE_URL` must use the driver suffix** `postgresql+psycopg://...`. The
  bare `postgresql://` scheme resolves to psycopg2 (not installed) and fails with
  `ModuleNotFoundError: No module named 'psycopg2'`.
- Run backend CLIs via the venv (`.venv\Scripts\alembic`, `.venv\Scripts\pytest`)
  or activate the venv first, otherwise the commands aren't on PATH.

## What's next

Iteration 03 introduces the **service layer** and API routes for the first
capability, using these repositories behind services (which will own the commit
boundary and DTOs).
