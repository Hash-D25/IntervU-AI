# app/features

Feature-based modules - the heart of the application. Each folder is one business
capability and owns its full vertical slice:

```
<feature>/
├── router.py       # validates requests, calls the service (thin)
├── service.py      # business logic (single responsibility)
├── repository.py   # data access (isolated; owns ORM models)
├── models.py       # SQLAlchemy ORM models (private to the feature)
├── dto.py          # Pydantic request/response + cross-layer DTOs
└── tests/          # unit tests for the service, etc.
```

Current capabilities:

- `resume/` - resume upload, parsing, and skill/project/experience extraction.
- `interview/` - interview session lifecycle + dynamic question flow.
- `evaluation/` - scoring answers across defined dimensions.
- `feedback/` - strengths, weaknesses, suggestions, and learning roadmap.

Dependencies point inward: features may use `core`, `db`, `shared`, and the
`ai` boundary - never each other's internals.
