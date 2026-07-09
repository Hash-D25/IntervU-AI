# app/core

Cross-cutting application concerns. **One responsibility: wiring, not business.**

Contents:

- `config.py` - typed settings loaded from env via `pydantic-settings`.
- `logging.py` - structured logging setup (`structlog`).
- `exceptions.py` - application-level exception types + handlers.
- `security/` - password hashing, JWT helpers, Google token verification.

No business logic and no database queries live here.
