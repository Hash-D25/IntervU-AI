# 03 - Authentication

## Goal

Add production-grade authentication - registration, login, JWT access tokens,
rotating refresh tokens, logout, and a reusable "protected route" dependency -
while keeping auth **isolated** from business logic.

## Scope

**In:** `core/security` (password hashing, JWT), `features/auth` (models,
schemas, repository, service, dependencies, router), `User.hashed_password`,
migration `0002_auth`, integration tests, config + deps.

**Out:** roles/permissions, email verification, password reset, rate limiting
(future iterations). Google SSO was added after this doc was written — see
`core/security/google.py` and `POST /auth/google`.

---

## Token strategy

- **Access token** - stateless **JWT** (HS256), ~15 min. Claims: `sub` (user id),
  `type=access`, `iat`, `exp`.
- **Refresh token** - **stateful, rotating**. An opaque random string
  (`secrets.token_urlsafe`) returned to the client; only its **SHA-256 hash** is
  stored in `refresh_tokens`. On `/refresh` the old token is revoked and a new
  one issued (rotation); `/logout` revokes it.

**Why stateful refresh:** revocable (real logout / "logout everywhere") and
rotation limits replay if a token leaks. **Tradeoff:** one indexed DB lookup per
refresh. **Alternative (rejected):** stateless JWT refresh - simpler but not
revocable.

**Why store only a hash:** a database compromise never yields usable refresh
tokens.

---

## Password hashing - Argon2id

`core/security/passwords.py` wraps `argon2-cffi` (`hash_password`,
`verify_password`). Argon2id is OWASP's current recommendation and avoids
bcrypt's 72-byte truncation. `verify_password` returns `False` on any Argon2
error instead of raising, so callers get a clean boolean.

---

## "Middleware" is a dependency

Token validation is a FastAPI **dependency** (`get_current_user` via
`HTTPBearer`), not ASGI middleware.

- **Why:** per-route, composable, typed (returns a `User`), and visible in the
  OpenAPI "Authorize" UI. Protecting any future route is just
  `current_user: CurrentUserDep`.
- Missing/invalid credentials → **401** (verified in tests).

---

## Layering & isolation

```
core/security/
├── passwords.py   # argon2 hash/verify
└── tokens.py      # JWT encode/decode, refresh generate/hash

features/auth/
├── models.py       # RefreshToken (hash only, expires_at, revoked_at)
├── schemas.py      # Register/Login/Refresh/Token/User DTOs (EmailStr)
├── repository.py   # RefreshTokenRepository (get_by_hash / get_active_by_hash / revoke)
├── service.py      # AuthService - register/login/refresh/logout
├── dependencies.py # DI providers + get_current_user + CurrentUserDep
└── router.py       # /auth routes
```

`hashed_password` lives on `User` (identity belongs to the user). Everything else
auth-specific stays in `features/auth`. Business features depend only on
`CurrentUserDep`.

### Transaction boundary

Repositories `flush`; **`AuthService` commits** via the injected `AsyncSession`.
This establishes the service-owns-commit pattern for all later features.

---

## Routes (`/api/v1/auth`)

| Method | Path | Body | Returns | Auth |
| ------ | ---- | ---- | ------- | ---- |
| POST | `/register` | RegisterRequest | UserResponse (201) | public |
| POST | `/login` | LoginRequest | TokenResponse | public |
| POST | `/refresh` | RefreshRequest | TokenResponse | public |
| POST | `/logout` | RefreshRequest | 204 | public |
| GET | `/me` | – | UserResponse | protected |

---

## Config & dependencies

New `Settings`: `jwt_secret_key`, `jwt_algorithm=HS256`,
`access_token_expire_minutes=15`, `refresh_token_expire_days=7`. New deps
(core group): `pyjwt`, `argon2-cffi`, `email-validator`.

**Secret handling:** a dev-only default secret exists so the app runs locally,
but **every real environment must set `JWT_SECRET_KEY`**. Generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Put it in `backend/.env` (gitignored). PyJWT warns if the key is < 32 bytes.

---

## Migration `0002_auth`

- `ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255) NOT NULL` (table was
  empty, so safe).
- `CREATE TABLE refresh_tokens` (`user_id` FK CASCADE, unique-indexed
  `token_hash`, `expires_at`, `revoked_at?`, timestamps).
- Offline-validated (`alembic upgrade head --sql`) and **applied to live
  Postgres** → `0002_auth (head)`.

---

## Testing

`tests/integration/test_auth.py` runs the full flow against in-memory SQLite
(StaticPool so the DB persists across requests) by overriding the `get_session`
dependency. Covered: register (no password echoed back), duplicate → 409, wrong
password → 401, `/me` with token → 200, `/me` without token → 401, refresh
rotation (old token → 401), logout revokes.

---

## Commands & verification

```bash
ruff check . && ruff format --check .   # All checks passed
mypy app                                # Success: 44 source files
pytest -q                               # 13 passed
alembic current                         # 0002_auth (head)
```

## Files

New: `core/security/{__init__,passwords,tokens}.py`,
`features/auth/{__init__,models,schemas,repository,service,dependencies,router}.py`
(+ README), `migrations/versions/0002_auth.py`,
`tests/integration/test_auth.py`.
Changed: `core/config.py` (JWT settings), `core/exceptions.py`
(`UnauthorizedError`, `ConflictError`), `features/user/models.py`
(`hashed_password`), `db/registry.py`, `api/v1/router.py`, `pyproject.toml`,
`backend/.env.example`.

## Notes & gotchas

- `HTTPBearer` returns **401** on missing credentials in this FastAPI version
  (tests assert 401).
- Refresh tokens are opaque, not JWTs - don't try to decode them; they're looked
  up by hash.
- The assistant does **not** auto-write secrets into `.env`; generate and add
  `JWT_SECRET_KEY` yourself (the dev default keeps local runs working).

## What's next

Iteration 04 begins real product features (e.g. resume upload/parsing), each
built as service + routes on top of the repositories, and protected with
`CurrentUserDep`.
