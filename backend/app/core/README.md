# app/core

Cross-cutting application concerns. **One responsibility: wiring, not business.**

Planned contents (added in later iterations):

- `config.py` - typed settings loaded from env via `pydantic-settings`.
- `logging.py` - structured logging setup (`structlog`).
- `exceptions.py` - application-level exception types + handlers.
- `di.py` - dependency-injection wiring (FastAPI `Depends` providers).

No business logic and no database queries live here.
