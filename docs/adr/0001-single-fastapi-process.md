# ADR-0001 — Single FastAPI process with layered routers

- **Status:** Accepted
- **Date:** unknown (reconstructed from code)

## Context

The platform exposes a wide surface — marketplace, wallet, escrow, contracts, logistics, payments, trading, news, AI agents, admin, notifications — and historically accumulated several entry-point files (`app_original.py`, `app_simple.py`). A decision was needed between a distributed service topology and a consolidated app.

## Decision

Ship the entire backend as **one FastAPI application** (`app.py`) with an internal layering discipline: `backend/api/` (HTTP contracts) → `services/` (business logic) → `core/` (cross-cutting platform) → `models.py`/`database.py` (persistence). Router modules are mounted with `app.include_router(...)`; older feature families are inline handlers in `app.py`.

## Consequences

+ Simple local development: one process, one port, one OpenAPI schema (183 paths).
+ Layering keeps unit testing feasible without infrastructure.
− No independent scaling or failure isolation per domain.
− Import graph is wide; a bad import can take down the whole process (mitigated by ADR-0002).
− Inline vs. router split is inconsistent (two response styles).

## Evidence

`app.py` (app factory + mounts), `backend/api/*` (16 routers), `services/`, `core/`, `docs/architecture.md`.
