# ADR-0005 — ESG scoring is deterministic and mock-data driven

- **Status:** Accepted (explicitly interim)
- **Date:** unknown (reconstructed from `services/esg_auditor.py`)

## Context

Product requirements call for per-listing ESG scores and carbon-neutral certificates backed by "satellite data". No satellite imagery provider is integrated, and the scoring must still be demonstrable and testable.

## Decision

`ESGAuditor` derives **deterministic mock satellite data** from the listing's coordinates (deforestation ≈ |latitude| × 0.1, reforestation ≈ |longitude| × 0.15, fixed per-km² carbon coefficients, derived quality indices), then computes environmental/social/governance scores, a carbon balance, a carbon-neutral tier, and a certificate. All formulas are documented in code and pinned by 34 regression tests. The `satellite_verification` flag is set `True` by the mock generator.

## Consequences

+ Reproducible scores; exact-value unit tests catch regressions (e.g. the `reforestation_area` field-name typo that silently broke scoring — commit `74e629a`, regression tests in `912c30e`).
+ No external API costs or flakiness in demos and tests.
− Scores are **not** real environmental measurements; `satellite_verified: true` in responses overstates provenance.
− Swapping in a real provider requires replacing `_generate_satellite_data` and re-pinning tests — deliberately isolated behind one method.

## Evidence

`services/esg_auditor.py` (`_generate_satellite_data`, scoring methods), `tests/unit/backend/test_esg_auditor.py` (34 tests), commits `74e629a` and `912c30e`.
