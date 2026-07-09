# tests

- `unit/` - fast, isolated tests for services and pure logic (no DB, no network).
- `integration/` - tests that exercise repositories, the API, and wiring.

Business logic is kept framework-agnostic so it can be unit-tested without
spinning up FastAPI or a database. Every important feature ships with tests.
