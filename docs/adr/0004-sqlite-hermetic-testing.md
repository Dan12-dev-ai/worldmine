# ADR-0004 — SQLite-first hermetic testing with dependency override

- **Status:** Accepted
- **Date:** unknown (reconstructed from `conftest.py`)

## Context

The API tests must run in CI and on developer machines without PostgreSQL, Redis, or Supabase. The app creates its SQLAlchemy engine at import time from `DATABASE_URL`, which couples test runs to whatever database the environment points at.

## Decision

The root `conftest.py`:

1. Sets `DATABASE_URL=sqlite:///./test_worldmine.db` **before** importing `database` (winning the import-time race).
2. Creates a dedicated in-memory SQLite engine (`StaticPool`, `check_same_thread=False`) with all tables created from `models.Base`.
3. Overrides the FastAPI `get_db` dependency and yields a session-scoped `TestClient`.
4. Skips tests marked `staging` unless `RUN_STAGING_TESTS=1`.

## Consequences

+ Fully hermetic, fast test runs — verified: 108 passed, 41 skipped with no services running.
+ Contributors need zero infrastructure to validate changes.
− Dialect differences (SQLite vs PostgreSQL) are not caught by the default suite.
− Any test constructing its own engine must replicate the override discipline.
− Tests importing `app` execute all import-time side effects (slow-ish startup).

## Evidence

`conftest.py` (root), `pyproject.toml` (`asyncio_mode = "auto"`, `staging` marker), verified suite output.
