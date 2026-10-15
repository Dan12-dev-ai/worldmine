<!-- README.md — World Mine (DEDAN Mine) -->
# World Mine

**An AI-assisted mineral trading marketplace platform: listings, escrow, contracts, logistics, ESG carbon scoring, and satellite-informed provenance — delivered as a FastAPI backend and a React single-page application.**

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18 + TypeScript](https://img.shields.io/badge/frontend-React%2018%20%2B%20TypeScript-61dafb.svg)](https://react.dev/)
[![Vite + PWA](https://img.shields.io/badge/build-Vite%20%2B%20PWA-646cff.svg)](https://vitejs.dev/)

**Live site (frontend):** [worldmine.vercel.app](https://worldmine.vercel.app) · **Interactive API docs:** served at `/docs` on the API host

[Overview](#overview) · [Capabilities](#core-capabilities) · [Architecture](#architecture) · [Quick start](#quick-start) · [Configuration](#configuration) · [Testing](#testing-and-quality-assurance) · [Docs](#documentation-index) · [Roadmap](#roadmap)

---

## At a glance

| | |
|---|---|
| **What it is** | A monolithic FastAPI application (`app.py`, version `3.0.0`) exposing 183 OpenAPI paths, plus a React 18 / TypeScript / Vite single-page app (`web-client/`) that talks to it over a same-origin `/api` proxy. |
| **Problem it addresses** | Mineral and gemstone trade is fragmented across small sellers, with thin digital tooling for verified provenance, escrowed payment, environmental (ESG) proof, and cross-border compliance. |
| **Who it is for** | Mineral/gemstone sellers and buyers, marketplace operators, and developers extending the platform. |
| **Current status** | Active development. Core read/write flows work locally (verified below); several modules are deliberately degraded or mocked and are labelled as such in [Core capabilities](#core-capabilities). |
| **License** | **Not yet chosen** — see [License and attribution](#license-and-attribution). |

## Overview

World Mine (the codebase still carries the earlier name **DEDAN Mine** in module names, titles, and API descriptions) combines four concerns in one platform:

1. **Trading** — mineral listings, auctions and buy-it-now, orders, wallets, payments, escrow, contracts, and logistics.
2. **Trust** — KYC hooks, per-listing traceability records, satellite verification stubs, and per-listing **ESG scoring with carbon-neutral certificates**.
3. **Automation** — AI-agent endpoints (negotiation, governance, monitoring, mineral news), an event bus, and reliability middleware.
4. **Client experience** — an installable PWA with marketplace browsing, a multi-module authenticated workspace, i18n, and a Three.js geological environment.

The design is a **single deployable process**: one FastAPI app serves JSON APIs, WebSocket endpoints, Swagger UI (`/docs`), ReDoc (`/redoc`), and the OpenAPI schema (`/openapi.json`). The frontend is a static build deployed separately (Vercel in production).

### What works today (verified by running the code)

The following was executed against a fresh checkout with **no external services** (no PostgreSQL, Redis, or Supabase):

```bash
DATABASE_URL=sqlite:///./worldmine.db python3 -c "from database import init_db; init_db()"
python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

| Check | Result |
|---|---|
| `GET /health` | `200` — `{"status": "healthy", ...}` |
| `GET /docs`, `GET /openapi.json` | `200` — 183 paths in the schema |
| `GET /api/marketplace/listings` | `200` — `{"data": [], "total": 0, ...}` (empty store, valid envelope) |
| `GET /api/v1/listings/browse` | `200` |
| `GET /api/trading/orders` | `200` — `[]` (in-memory, seeded/mocked rows only) |
| `GET /api/v2/mineral-news/` | `200` |
| `POST /api/v4/esg/calculate-carbon-neutral-score` | `200` — deterministic ESG score with satellite data payload |
| Backend test suite (`pytest tests`) | **108 passed, 41 skipped** (skips require live staging infra) |
| Frontend typecheck (`npx tsc --noEmit`) | **0 errors** |

Flows that need external services (Supabase-backed auth, Redis, SendGrid, PostgreSQL-specific behaviour, live payments) are **not** covered by this list and are marked *Partial* or *Unverified* below.

---

## Core capabilities

Status key: **Implemented** = works and is exercised by tests or manual verification · **Partial** = present but degraded (mocked data, in-memory state, or missing dependency) · **Planned** = designed/stubbed only · **Unverified** = code exists but was not exercised.

| Capability | Description | Status | Where | Evidence |
|---|---|---|---|---|
| Marketplace listings | CRUD + paginated browse of mineral listings (auction / buy-it-now) | Implemented | `backend/api/marketplace.py`, `services/marketplace/listings.py` | `GET /api/marketplace/listings` → 200 after `init_db()` |
| ESG carbon scoring | Deterministic environmental/social/governance score + carbon-neutral level + certificate per listing | Implemented | `services/esg_auditor.py`, `/api/v4/esg/*` | 34 unit tests (`tests/unit/backend/test_esg_auditor.py`); live POST verified |
| Wallet & payments API | Wallet endpoints + payment router (Chapa/Telebirr-shaped integration points) | Partial | `backend/api/wallet.py`, `backend/api/payment.py` | Router mounted; real payment rails need credentials |
| Escrow, contracts, logistics, notifications, admin | Full endpoint surface | Partial | `backend/api/{escrow,contracts,logistics,notifications,admin}.py` | State kept in **module-level dicts** (lost on restart) — screens say so |
| Trading | Orders, trades, performance | Partial | `backend/api/trading.py` | Serves seeded/mocked rows; auth is a placeholder dependency |
| Mineral news | Aggregated/analysed market news API | Partial | `backend/api/mineral_news_api.py` | Mounted (`/api/v2/mineral-news/` → 200); enrichment needs API keys |
| Auth (JWT + Supabase) | Registration, login, magic links, JWT bearer auth | Partial | `backend/api/auth.py` | Needs `SUPABASE_URL`, Redis, SendGrid — not exercised locally |
| KYC document checks | Document upload verification | Partial (not mounted) | `backend/api/kyc.py` | Router **deliberately not mounted**: imports `cv2`, which is absent; see `app.py` comment |
| Sovereign / next-gen auth | FIDO2, SSI/DID, post-quantum, zero-knowledge, behavioural, liveness endpoints | Unverified | `/api/v4/auth/*`, `/api/v4/sovereign/*` | Endpoints return mock verifications; `webauthn`/`liboqs` not installed |
| Traceability & satellite | Sensor registration, coordinate verification, provenance records | Partial | `/api/v1/traceability/*`, `/api/v3/satellite/*` | Stubs with deterministic mock calculations |
| AI agents | Agent create/analyse/bid, governance, monitoring, video negotiation | Partial | `backend/api/ai_*.py`, `services/video_negotiation.py` | Mounted; heavy integrations degrade gracefully (503 when deps missing) |
| Frontend SPA (PWA) | Landing, news, content pages, marketplace, mineral detail, auth, 8-module workspace, admin | Implemented | `web-client/` | `tsc --noEmit` = 0 errors; production build passes; honest empty/error states in `DataPanel.tsx` |
| Realtime | WebSocket gateway | Partial | `backend/websocket/gateway.py` | Router mounted; not load-tested here |
| Reliability middleware | Rate limiting, health, structured errors | Implemented | `backend/api/reliability_middleware.py`, `core/reliability_system.py` | Part of the app pipeline |

## Architecture

One process, three layers: **HTTP/WS edge (FastAPI)** → **routers (`backend/api/`)** → **services (`services/`, `core/`)**, persisted through **SQLAlchemy (`models.py`, 24 tables)** with an in-memory fallback for state that has not been modelled yet.

```mermaid
flowchart LR
    subgraph Client["Browser / PWA"]
        UI["web-client (React 18 + TS + Vite)<br/>marketplace · workspace · admin"]
    end

    subgraph API["FastAPI process (app.py :8000)"]
        MW["Middleware<br/>CORS · GZip · TrustedHost"]
        R1["Routers: backend/api/*<br/>marketplace · wallet · escrow · contracts<br/>logistics · payment · trading · news · ai_*"]
        R2["Inline routers: app.py<br/>/api/v4/esg · /api/v4/auth · /api/v3/* · /api/v4/tax"]
        SVC["Services & core<br/>services/* · core/*<br/>(ESG, marketplace, video, IoT, ECX…)"]
    end

    DB[("SQLAlchemy<br/>PostgreSQL / SQLite<br/>models.py (24 tables)")]
    MEM[("In-memory module dicts<br/>escrow · contracts · logistics<br/>notifications · admin · trading")]
    EXT[("External (optional)<br/>Supabase · Redis · SendGrid<br/>Chapa · AI providers")]

    UI -- "HTTPS /api (Vite proxy in dev)" --> MW
    MW --> R1 & R2
    R1 & R2 --> SVC
    SVC --> DB
    SVC -.-> MEM
    SVC -.-> EXT
```

Key properties: routers are thin (validation + delegation); services own business logic; `core/` holds cross-cutting systems (unified state manager, sovereign auth, conflict prevention, event-driven architecture, health monitor); optional integrations are import-guarded so the app **boots without them** and returns `503` from the affected endpoints only. Full detail, request lifecycle, and constraints: [docs/architecture.md](docs/architecture.md).


---

## Technology stack

Verified from dependency manifests and runtime configuration (`requirements.txt`, `runtime.txt`, `web-client/package.json`).

| Layer | Technology |
|---|---|
| Language & runtime | Python 3.11 (`runtime.txt`), Node 18+ for frontend tooling |
| API framework | FastAPI + Uvicorn (ASGI), Pydantic models, JWT (`pyjwt`), `bcrypt` |
| Persistence | SQLAlchemy ORM — 24 tables in `models.py`; PostgreSQL in production, SQLite for local/tests |
| Cache / queues | Redis (optional; in-memory fallbacks) |
| AI & data (optional) | `langchain`, `langgraph`, `google-generativeai`, `anthropic`, `supabase`, `tavily-python` |
| Frontend | React 18, TypeScript 5, Vite 4, React Router 6, TanStack Query (react-query v3), Zustand, Tailwind CSS, MUI + Radix UI, Framer Motion, Recharts, Three.js, i18next, `vite-plugin-pwa` |
| Testing | pytest (+ `pytest-asyncio`, `pytest-cov`, `httpx` TestClient), ESLint + `tsc --noEmit` for the frontend |
| Deployment | Render (`render.yaml` → `uvicorn app:app`), Vercel (static frontend), Docker (`Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.dev.yml`) |
| Observability | Structured logging, `sentry-sdk` (optional), Prometheus client (optional) |

## Quick start

All commands are run from the repository root and were executed on Linux. Python 3.11+ and (for the frontend) Node 18+ are required.

### 1. Backend, zero-dependency mode (no PostgreSQL/Redis/Supabase)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create the schema in a local SQLite file
DATABASE_URL=sqlite:///./worldmine.db python3 -c "from database import init_db; init_db()"

# Boot the API (SQLite again, so the app finds the same schema)
DATABASE_URL=sqlite:///./worldmine.db python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Smoke test:

```bash
curl -s http://127.0.0.1:8000/health          # -> {"status": "healthy", ...}
open http://127.0.0.1:8000/docs              # Swagger UI, 183 paths
```

> **Note:** `init_db()` must run with the **same** `DATABASE_URL` the server will use; otherwise endpoints that touch tables return `500 no such table`. This is the most common first-run failure — see [docs/troubleshooting.md](docs/troubleshooting.md).

### 2. Frontend dev server

```bash
cd web-client
npm install
npm run dev          # Vite on :5173; proxies /api to 127.0.0.1:8000
```

Production build and preview (proxies `/api` to the API host; override target with `VITE_API_TARGET`):

```bash
npm run build        # tsc && vite build -> dist/
npx vite preview --port 4173 --strictPort
```

### 3. Docker (alternative)

`docker-compose.dev.yml` defines an API + supporting services. **Not verified in this audit** — treat as a starting point, not a guaranteed path.

Full setup, environment matrix, and common failures: **[docs/getting-started.md](docs/getting-started.md)**.


---

## Configuration

Environment variables are read via `python-dotenv` (`database.py` calls `load_dotenv()`). `.env.example` at the repository root is the template — copy it to `.env` and fill in values. **Never commit `.env`.** Full reference: [docs/configuration.md](docs/configuration.md).

Core variables actually read by the boot path:

| Variable | Purpose | Required | Default | Example |
|---|---|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string (PostgreSQL or SQLite) | Yes (has fallback) | `postgresql://dedanmine:password@localhost:5432/dedanmine` | `sqlite:///./worldmine.db` |
| `JWT_SECRET` | HS256 signing key for API JWTs | **Yes in production** | insecure dev placeholder | long random string |
| `PRODUCTION_URL` | The single origin allowed by CORS | No | `https://worldmine.vercel.app` | `https://your-app.vercel.app` |
| `ENVIRONMENT` | `development` / `production` switch, reported by `/health` | No | `production` | `development` |
| `REDIS_HOST` / `REDIS_PORT` / `REDIS_URL` | Redis for sessions/rate limits (optional) | No | `localhost` / `6379` | `redis://redis:6379` |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | Supabase-backed auth in `backend/api/auth.py` | Only for auth router | — | `https://xyz.supabase.co` |
| `SENDGRID_API_KEY` | Transactional email (auth router) | Only for auth router | — | `SG.…` |
| `DEBUG` | SQLAlchemy echo + verbose logging | No | `false` | `true` |
| `PORT` / `HOST` | Uvicorn bind (used by deployment configs) | No | `8000` / `0.0.0.0` | — |

`.env.example` additionally declares integration keys (OpenAI/Anthropic/Groq, Binance, Chapa, Telebirr). Those are consumed by optional services, not by the boot path; the app starts without them.

## Usage examples

Verified against a locally running instance (see [What works today](#what-works-today-verified-by-running-the-code)).

**ESG carbon-neutral score** — deterministic, no external services:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v4/esg/calculate-carbon-neutral-score \
  -H 'Content-Type: application/json' \
  -d '{"listing_data": {"listing_id": "demo-1", "mineral_type": "gold",
       "location": {"latitude": 9.0, "longitude": 38.0}}}'
```

```json
{
  "success": true,
  "listing_id": "demo-1",
  "esg_score": {
    "overall_score": 83.9,
    "environmental_score": 59.74,
    "social_score": 100,
    "governance_score": 100,
    "carbon_neutral_level": "carbon_aware",
    "carbon_balance": 195.0,
    "satellite_verified": true
  }
}
```

**Certificate for the same listing:**

```bash
curl -s http://127.0.0.1:8000/api/v4/esg/certificate/demo-1
```

**Marketplace browse** (valid, empty envelope on a fresh database):

```bash
curl -s 'http://127.0.0.1:8000/api/marketplace/listings?page=1&page_size=20'
# {"data": [], "total": 0, "page": 1, "page_size": 20, "has_next": false, "has_previous": false}
```

The complete, machine-readable API surface is at `GET /openapi.json`; browse it at `/docs` (Swagger UI) or `/redoc`.

## Testing and quality assurance

| Check | Command | Last verified result |
|---|---|---|
| Backend unit + integration tests | `python3 -m pytest tests` | **108 passed, 41 skipped** (skips are `staging`-marked; set `RUN_STAGING_TESTS=1` to enable) |
| ESG regression suite | `python3 -m pytest tests/unit/backend/test_esg_auditor.py` | 34 passed |
| Frontend typecheck | `cd web-client && npx tsc --noEmit` | 0 errors |
| Frontend lint | `cd web-client && npm run lint` | configured (`eslint . --max-warnings 0`) |
| Frontend production build | `cd web-client && npm run build` | passes (tsc + Vite + PWA service worker) |

Test infrastructure: root `conftest.py` provides a `TestClient` backed by an **in-memory SQLite** database with the `get_db` dependency overridden, so the API tests run hermetically. Integration tests that require live infrastructure are skipped by default via the `staging` marker.

> **Known CI gap:** the existing workflow `.github/workflows/ci-cd.yml` runs `npm ci` at the repository root, which has **no `package.json`** (frontend lives in `web-client/`), and references an `npm run test:coverage` script that does not exist. CI as committed is expected to fail; see [docs/testing.md](docs/testing.md) for details and a proposed fix. Backend tests are **not** covered by CI at all.

Security notes, secret handling, and threat boundaries: [docs/security.md](docs/security.md).


---

## Security

**Implemented:** CORS locked to `PRODUCTION_URL` + localhost dev origins (`cors_config.py`); JWT bearer auth with HS256; bcrypt password hashing; `.env.example` contains placeholders only; `.gitignore` excludes `.env`; optional Supabase RLS policies in `database/rls_policies.py`.

**Known concerns (honest list):** `JWT_SECRET` falls back to a placeholder if unset; several modules hold state in memory (no audit durability); KYC verification is not mounted; the sovereign-auth endpoints currently return mock verifications. See [docs/security.md](docs/security.md) for the full inventory, secret-handling rules, and how to report vulnerabilities privately via GitHub Security Advisories.

## Roadmap

Derived from verified gaps in this audit — no dates are committed.

**Completed:** conflict-free unified app skeleton with 183 OpenAPI paths; marketplace + ESG scoring with regression tests; frontend rebuild (typecheck/lint/build green) with honest data states; routers for trading and mineral news mounted.

**In progress / next:**
1. Fix CI (point frontend jobs at `web-client/`, add a backend pytest job) — [docs/testing.md](docs/testing.md).
2. Persist the in-memory stores (escrow, contracts, logistics, notifications, admin, trading) into SQLAlchemy models before any real money moves.
3. Mount the KYC router (headless OpenCV) or remove the dead dependency.
4. Replace mock sovereign-auth verifications with real FIDO2/PQC libraries, or label the endpoints experimental in the OpenAPI schema.
5. Add a `role` claim to `/api/auth/me` so the frontend admin gate can be verified end-to-end.
6. Decide the license (see below).

**Longer-term possibilities:** real satellite/AI provider integrations behind the existing service interfaces, deal-room chat/documents, measured (not seeded) admin analytics.

## Contributing

Contributions are welcome. Setup, branch naming, conventions, and the pull-request checklist live in [CONTRIBUTING.md](CONTRIBUTING.md). In short: fork → feature branch → keep the suite green (`pytest tests`, `tsc --noEmit`) → open a PR using the template. Security issues go through [SECURITY.md](SECURITY.md), never a public issue.

## Documentation index

| Document | Contents |
|---|---|
| [docs/README.md](docs/README.md) | Documentation hub and map |
| [docs/getting-started.md](docs/getting-started.md) | Install, configure, run, verify — with failure modes |
| [docs/architecture.md](docs/architecture.md) | Components, request lifecycle, data flow, diagrams, constraints |
| [docs/project-structure.md](docs/project-structure.md) | What every top-level directory and file is for |
| [docs/configuration.md](docs/configuration.md) | Complete environment-variable reference |
| [docs/development.md](docs/development.md) | Local dev workflow, conventions, debugging |
| [docs/testing.md](docs/testing.md) | Test suite layout, commands, CI status and gaps |
| [docs/deployment.md](docs/deployment.md) | Render/Vercel/Docker paths, health checks, limits |
| [docs/security.md](docs/security.md) | Controls, secrets, boundaries, reporting |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Real observed failures and fixes |
| [docs/faq.md](docs/faq.md) · [docs/glossary.md](docs/glossary.md) | FAQ and terminology |
| [docs/adr/README.md](docs/adr/README.md) | Architecture decision records |
| [CONTRIBUTING.md](CONTRIBUTING.md) · [SECURITY.md](SECURITY.md) · [SUPPORT.md](SUPPORT.md) | Community documents |

Historical audit reports (root `*.md` and `docs/QA_REPORT.md` etc.) are indexed — with freshness warnings — in [docs/README.md](docs/README.md#historical-documents).

## License and attribution

**This repository currently has no license file.** Without one, the code is legally all-rights-reserved and cannot be reused or contributed to under standard terms. Choosing a license is an explicit decision for the repository owner — it has deliberately not been assumed here. Recommended next step: add a `LICENSE` (e.g., MIT for permissive adoption, or Apache-2.0 for patent protection) and the matching badge.

Project history: built under the DEDAN Mine name; deployed frontend at [worldmine.vercel.app](https://worldmine.vercel.app). No affiliation with any exchange or standards body is claimed or implied by this documentation.


