# Glossary

Project-specific terms as used **in this repository**. Where a term differs from its generic industry meaning, the local meaning is stated.

| Term | Definition |
|---|---|
| **World Mine / DEDAN Mine** | The product. "World Mine" is the current name; "DEDAN Mine" persists in code identifiers, API titles, and older docs. Both refer to this codebase. |
| **Carbon-neutral level** | Tier assigned by `ESGAuditor` from the carbon balance: `carbon_negative` (≤ −100 t), `carbon_neutral` (≤ 0), `low_carbon` (≤ 50), `carbon_aware` (≤ 200), `carbon_untracked` (> 200). |
| **Carbon balance** | `carbon_sequestered − carbon_emitted` in tons CO₂ for a listing's location (negative = net removal). |
| **ECX** | Ethiopia Commodity Exchange. `ECXComplianceService` models exchange-compliance checks for listings. |
| **ESG score** | Weighted score: environmental 40 %, social 30 %, governance 30 %, each 0–100, computed per listing (`services/esg_auditor.py`, `services/esg/`). |
| **FeatureGuard** | The frontend router guard (`web-client/src/app/router/FeatureGuard.tsx`) that fails closed when the session lacks a capability. |
| **Guardian AI Vault** | `services/unified/GuardianAIVault.py` — user-data protection/monitoring service (v3 feature family). |
| **In-memory store** | Module-level Python dicts used by escrow, contracts, logistics, notifications, admin, trading routers. Functional but lost on restart. |
| **Legacy success-flag** | Response style `{"success": true/false, "error": ...}` used by inline `/api/v3`, `/api/v4` endpoints, as opposed to the **data envelope** (`{"data": [...], "total": n}`) used by routers. |
| **Micro-insurance oracle** | `services/unified/MicroInsuranceOracle.py` — premium/claims calculations, ESG-adjusted. |
| **Mineral news** | Market-news aggregation and analysis API (`/api/v2/mineral-news`). |
| **Module (workspace)** | One authenticated frontend screen family (Deals, Contracts, Escrow, Logistics, Messages, Profile, Security, Admin) under `web-client/src/features/workspace/`. |
| **Sovereign auth** | The `/api/v4/sovereign/*` + `/api/v4/auth/*` family: invisible handshake, digital key, behavioural DNA, FIDO2, SSI/DID, post-quantum, ZK, liveness. Currently mocked. |
| **Staging marker** | pytest marker for tests needing live infrastructure; skipped unless `RUN_STAGING_TESTS=1`. |
| **Traceability record** | Per-listing provenance entry (`traceability_records` table) produced by `/api/v1/traceability/*`. |
| **Unified state manager** | `core/StateManagement.py` — single source of truth for cross-cutting platform state. |
| **Video negotiation** | `services/video_negotiation.py` + `/api/v1/video/*` — scheduled negotiation sessions between parties. |
