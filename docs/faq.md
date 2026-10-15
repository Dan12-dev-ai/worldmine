# FAQ

**What is World Mine?**
A marketplace platform for minerals and gemstones: listings, auctions, escrow-shaped workflows, contracts, logistics, per-listing ESG carbon scoring, and traceability records. FastAPI backend + React PWA. The codebase still uses the earlier name *DEDAN Mine* in many identifiers.

**Is it production-ready?**
Partially. Core marketplace reads/writes and ESG scoring work and are tested. Several money-adjacent modules (escrow, contracts, logistics) keep state in memory, auth relies on optional external services, and CI is misconfigured. See the roadmap in the root [README](../README.md#roadmap) and the constraints in [architecture.md](architecture.md#8-known-architectural-constraints-verified).

**Why do some screens say data is mocked or in-memory?**
Because it is. The platform's documentation standard is honesty: the UI states when data is seeded, degraded, or volatile instead of presenting it as verified history.

**Do I need PostgreSQL/Redis/Supabase to run it locally?**
No. SQLite mode is fully supported for development ([getting-started.md](getting-started.md)). Supabase/Redis/SendGrid are needed only for the auth router; AI/payment keys only for those integrations.

**Where is the API reference?**
Interactive Swagger UI at `/docs` on a running server; machine-readable schema at `/openapi.json` (183 paths). A static `backend/api/openapi.yaml` also exists but may lag the live schema.

**Why are there two API styles (`{"data": ...}` and `{"success": ...}`)?**
Historical layering: routers built later use FastAPI-native envelopes; the inline `/api/v3`, `/api/v4` endpoints use a legacy success-flag payload. The frontend types both. Consolidation is a future decision, not an accident to "fix" casually.

**What does the ESG score actually measure?**
An environmental/social/governance score derived from listing coordinates via documented deterministic formulas (deforestation/reforestation proxies, water/air/biodiversity indices), a carbon balance, and a carbon-neutral level (carbon_negative → carbon_untracked). It is a **modelled** score from mock satellite math — not live satellite imagery. See `services/esg_auditor.py` and its 34 regression tests.

**Why is the KYC endpoint missing?**
The KYC router imports OpenCV (`cv2`), which is not installed; the router is deliberately unmounted (comment in `app.py`). Install `opencv-python-headless` and mount it if needed.

**Can I contribute?**
Yes — see [../CONTRIBUTING.md](../CONTRIBUTING.md). Documentation-only contributions are as valuable as code.

**How do I report a security issue?**
Privately via GitHub Security Advisories — see [security.md](security.md#reporting-a-vulnerability). Never in a public issue.

**Which license is it?**
None yet — the repository has no LICENSE file. That is an open decision for the owner ([../README.md](../README.md#license-and-attribution)).
