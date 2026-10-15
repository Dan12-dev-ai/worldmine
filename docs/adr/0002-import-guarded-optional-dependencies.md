# ADR-0002 — Optional integrations are import-guarded; process must always boot

- **Status:** Accepted
- **Date:** unknown (reconstructed from code and comments)

## Context

`requirements.txt` lists many optional providers (Supabase SDK, AI providers, WebAuthn, liboqs, OpenCV). In several deployment and developer environments these packages or their credentials are unavailable. A hard import dependency would prevent the API from starting at all.

## Decision

Wrap optional imports in `try/except` at the application edge (`app.py`), store the resulting class/client as `None` when unavailable, and have the affected endpoints return **503** with an explanatory body. The process must boot regardless of which optional integrations are present.

## Consequences

+ Guaranteed startup; health endpoints remain available for orchestration.
+ Partial deployments degrade at the endpoint, not the platform.
− Import-time failures surface late (on first call) rather than at deploy time.
− A typo in an optional import can silently disable a feature until someone calls it.
− The auth router (`backend/api/auth.py`) is a documented exception — it hard-requires Supabase/Redis/SendGrid at import and is therefore not mounted by default (ADR-0003 pattern applied to it as well).

## Evidence

`app.py` (`_load_trading_agent_cls`, `SimpleMarketNewsAgent` guard, "Optional agents" comment), 503 handling in optional endpoints, `docs/security.md`.
