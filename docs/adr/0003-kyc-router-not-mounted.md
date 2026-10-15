# ADR-0003 — KYC router deliberately not mounted (OpenCV dependency)

- **Status:** Accepted
- **Date:** 2026-09 (commit-era; see comment in `app.py`)

## Context

`backend/api/kyc.py` implements KYC document verification and imports `cv2` (OpenCV) at module import. OpenCV is absent in the target environments, so importing the router raises `ModuleNotFoundError` and would crash app startup.

## Decision

Do **not** mount the KYC router. Document the omission with an explicit comment at the router-import block in `app.py`, and state the consequence in product documentation (KYC features are unavailable; do not claim KYC verification).

## Consequences

+ App boots in minimal environments.
− `/api/kyc/*` endpoints do not exist in the running API and are absent from `/openapi.json`.
− KYC-dependent copy or UI flows must be labelled unavailable.
− Re-enabling requires `opencv-python-headless` and a one-line mount — low cost, but untested since the decision.

## Evidence

Comment in `app.py` above router imports ("backend.api.kyc is intentionally NOT mounted — it imports cv2"); `ModuleNotFoundError: No module named 'cv2'` reproduced on demand; README capability matrix.
