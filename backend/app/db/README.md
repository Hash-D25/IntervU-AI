# app/db

Database infrastructure only. **One responsibility: connections + session lifecycle.**

Planned contents:

- `engine.py` - SQLAlchemy 2 async engine.
- `session.py` - session factory + request-scoped session dependency.
- `base.py` - declarative base for ORM models.

ORM models themselves live inside each feature (`features/<name>/models.py`)
and are only ever touched by that feature's repository.
