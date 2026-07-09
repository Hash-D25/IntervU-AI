# features/auth

Authentication, isolated from business logic.

Responsibility: registration, login, token issuance/rotation, logout, and the
`get_current_user` dependency that protects routes. Business features depend only
on that dependency - never on auth internals.

- `models.py` - `RefreshToken` (stateful, rotating; stores only a hash).
- `schemas.py` - request/response DTOs.
- `repository.py` - `RefreshTokenRepository`.
- `service.py` - `AuthService` (owns the commit boundary).
- `dependencies.py` - DI providers + `get_current_user` / `CurrentUserDep`.
- `router.py` - `/auth` routes.

Crypto primitives (password hashing, JWT) live in `app/core/security`.
