# Architecture decision records (ADRs)

Lightweight ADRs capturing decisions that are **recoverable from repository evidence**. Rationale is marked *[reconstructed]* where it is inferred from code/comments rather than documented history.

## Format

Each ADR: `NNNN-kebab-title.md` with **Status** (Proposed / Accepted / Superseded / Amended), **Context**, **Decision**, **Consequences**, and **Evidence** (files/commits). Keep them under a page.

## Index

### [0001 — Single FastAPI process with layered routers](0001-single-fastapi-process.md)
Accepted. The whole platform ships as one ASGI app (`app.py`) with routers → services → core layering, despite a large endpoint surface.

### [0002 — Optional integrations are import-guarded; process must always boot](0002-import-guarded-optional-dependencies.md)
Accepted. Optional agents/providers fail soft (503 on affected endpoints) rather than crashing startup.

### [0003 — KYC router deliberately not mounted (OpenCV dependency)](0003-kyc-router-not-mounted.md)
Accepted, with a known cost: `/api/kyc/*` is absent from the running API.

### [0004 — SQLite-first hermetic testing with dependency override](0004-sqlite-hermetic-testing.md)
Accepted. Tests run against in-memory SQLite via FastAPI dependency overrides; live-infra tests are opt-in via the `staging` marker.

### [0005 — ESG scoring is deterministic and mock-data driven](0005-deterministic-esg-scoring.md)
Accepted for now. Satellite data is generated from listing coordinates by documented formulas; real satellite integration is future work.

## Template for new ADRs

```markdown
# NNNN — Title

- **Status:** Proposed | Accepted | Superseded by NNNN | Amended
- **Date:** YYYY-MM-DD (if known; otherwise "unknown (reconstructed)")

## Context
What problem or force required a decision?

## Decision
What was decided, in one or two sentences.

## Consequences
Positive, negative, and neutral effects. What becomes harder later?

## Evidence
Files, endpoints, commits, or tests that corroborate this record.
```

When adding an ADR: increment the index here, reference it from relevant docs, and never rewrite history — supersede instead.
