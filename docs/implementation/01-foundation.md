# 01 - Project Foundation

## Goal

Turn the empty scaffold into a **runnable, tested foundation**: the backend
boots, loads typed config, connects to Postgres, exposes a health check, and has
async migrations ready; the frontend renders with React Query and a typed API
client. **No business logic.**

## Scope

**In:** config, structured logging, exceptions, DI wiring, async DB engine +
session, app factory + lifespan, versioned API router, health endpoint, Alembic
(async), a health test, frontend layout/providers/API client, the AI provider
*contract*.

**Out:** resume/interview/evaluation/feedback logic, AI implementations, auth,
voice, any database tables.

---

## Architecture & decisions

### App factory + lifespan

`create_app()` builds the FastAPI instance; an `asynccontextmanager` lifespan
creates the DB engine and session factory on startup and disposes the engine on
shutdown, storing both on `app.state`.

- **Why a factory:** tests build isolated app instances and can override
  dependencies; no module-level global app to fight with.
- **Why `app.state`:** the session dependency reads the factory from
  `request.app.state`, so swapping the engine in tests needs no monkeypatching
  of module globals.
- **Alternative:** module-level `app = FastAPI()`. Simpler, but worse for
  testing and lifecycle control.

### Configuration via pydantic-settings + DI

A single `Settings(BaseSettings)` reads env vars (and `.env`), validated once.
`get_settings()` is `lru_cache`d and injected with `Depends`.

- **Why:** nothing reads `os.environ` directly; config is typed and testable.
- **Field naming:** field names map case-insensitively to env vars
  (`database_url` ← `DATABASE_URL`).

### Dependency injection = native FastAPI `Depends`

`core/container.py` exposes `Annotated` aliases:

```python
SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

- **Why:** explicit, type-safe, zero extra dependencies or "magic".
- **Alternative:** a DI framework (`dependency-injector`). Deferred - only worth
  it if wiring becomes unwieldy; adoptable later without rework.

### Async SQLAlchemy 2 + request-scoped session

`create_engine()` builds an `AsyncEngine` (`pool_pre_ping=True`).
`create_session_factory()` returns an `async_sessionmaker`
(`expire_on_commit=False`). `get_session()` yields a session per request inside
`async with`, guaranteeing cleanup.

- **Why async:** non-blocking under FastAPI and a natural fit for future
  streaming AI calls.
- **Why `expire_on_commit=False`:** objects stay usable after commit (common
  need when returning data from services).

### Declarative base with naming convention

`db/base.py` defines `Base(DeclarativeBase)` with a `MetaData` naming
convention (`ix/uq/ck/fk/pk`).

- **Why:** deterministic constraint names make Alembic autogenerate stable and
  diffs clean across environments.

### API versioning

`main` mounts `api_router` under `settings.api_v1_prefix` (`/api/v1`).
`api_router → v1_router → health.router`. New features mount on `v1_router`.

- **Why the layering:** a single, obvious place to add versions and features
  without touching `main`.

### Errors

`core/exceptions.py` defines `AppError` (with `status_code`) and `NotFoundError`,
plus `register_exception_handlers()` that maps them to JSON responses.

- **Why:** services raise domain errors; the API layer doesn't hand-roll error
  responses. (The one `type: ignore` we tried was unnecessary and removed -
  FastAPI's handler typing is broad but our narrower handler is safe.)

### Logging

`core/logging.py` configures **structlog** with ISO timestamps, log level, and
**JSON** output. Called once in `create_app()`.

- **Why JSON:** machine-parseable logs for production.

### AI provider contract (no implementation)

`ai/providers/base.py` defines a `LLMProvider` **Protocol** with
`async generate(messages: Sequence[ChatMessage]) -> str`, plus a frozen
`ChatMessage` dataclass and a `Role` literal.

- **Why now:** satisfies "prepare for AI integrations" and "keep providers
  replaceable" - business logic will depend on this interface, never an SDK.
- **Why a `Protocol`:** structural typing means an implementation just needs the
  right shape; no base class to inherit.

### Alembic (async)

`migrations/env.py` pulls the URL from `Settings`, uses `Base.metadata` as
`target_metadata`, and runs migrations over an async engine via
`connection.run_sync`. `alembic.ini` leaves `sqlalchemy.url` blank (resolved at
runtime) and formats generated files with ruff.

- **Why URL from settings:** one source of truth; no duplicated connection
  strings.
- **Note:** the "import your models here" comment marks where feature models get
  registered so autogenerate can see them.

---

## File-by-file walkthrough

### Backend

| File | Responsibility |
| ---- | -------------- |
| `app/core/config.py` | `Settings` + cached `get_settings()`. |
| `app/core/logging.py` | `configure_logging(level)` (structlog JSON). |
| `app/core/exceptions.py` | `AppError`, `NotFoundError`, handler registration. |
| `app/core/container.py` | `SettingsDep`, `SessionDep` DI aliases. |
| `app/db/base.py` | `Base` + naming convention. |
| `app/db/engine.py` | `create_engine(url) -> AsyncEngine`. |
| `app/db/session.py` | session factory + `get_session` request dependency. |
| `app/api/router.py` | top-level `api_router`. |
| `app/api/v1/router.py` | `v1_router`, mounts feature routers. |
| `app/api/v1/health.py` | `GET /health` → `{"status": "ok"}`. |
| `app/ai/providers/base.py` | `LLMProvider` Protocol + `ChatMessage`. |
| `app/shared/types.py` | recursive `JSONValue` / `JSONObject` (PEP 695 `type`). |
| `app/main.py` | `create_app()` factory + `lifespan`. |
| `alembic.ini`, `migrations/env.py`, `migrations/script.py.mako` | async migrations. |
| `tests/conftest.py` | `app` + httpx `client` fixtures (in-process ASGI). |
| `tests/unit/test_health.py` | asserts `/api/v1/health` returns `ok`. |

### Frontend

| File | Responsibility |
| ---- | -------------- |
| `src/env.ts` | typed public env (`apiBaseUrl`, with dev fallback). |
| `src/lib/query-client.ts` | `createQueryClient()` factory (fresh cache per session). |
| `src/lib/api-client.ts` | typed `fetch` wrapper + `ApiError`. |
| `src/app/globals.css` | Tailwind directives. |
| `src/app/providers.tsx` | client component wrapping `QueryClientProvider`. |
| `src/app/layout.tsx` | root layout + metadata + providers. |
| `src/app/page.tsx` | placeholder landing page. |
| `.eslintrc.json` | `next/core-web-vitals`. |

---

## Commands & verification

```bash
# backend (from backend/, venv active)
ruff check .          # All checks passed
mypy app              # Success: no issues found in 21 source files
pytest -q             # 1 passed

# frontend (from frontend/)
npm run typecheck     # tsc --noEmit - clean
```

All four gates are green.

---

## How to run

```bash
docker compose up -d                          # Postgres + Chroma
cd backend && .venv\Scripts\activate
uvicorn app.main:app --reload                 # http://localhost:8000/docs
                                              # health: /api/v1/health
cd frontend && npm run dev                    # http://localhost:3000
```

---

## Notes & gotchas

- **No first migration yet** - there are no models, so
  `alembic revision --autogenerate` comes with the first feature that has a
  table. `alembic upgrade head` needs Postgres running; not yet verified against
  a live DB.
- **ESLint** uses `.eslintrc.json` (which `next lint` reads reliably) instead of
  an ESLint 9 flat config, to avoid flat-config friction with Next 15.
- **`next-env.d.ts`** is generated by Next on first `dev`/`build`; not committed
  by hand.
- The health endpoint is intentionally **infrastructure, not business logic** -
  it exists to prove the foundation works and to support CI/liveness probes.

## What's next

Iteration 02 will introduce the first real feature. Following the project rule,
it will start with an architecture proposal (tradeoffs + alternatives) and wait
for approval before any code.
