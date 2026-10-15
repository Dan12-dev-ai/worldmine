# Project structure

An annotated map of the repository as it exists. Only directories that are part of the running system or its verification tooling are described in depth; the long tail of historical files is summarised at the end.

```
worldmine/
├── app.py                  # FastAPI entry point: app factory, ~50 inline endpoints,
│                           #   middleware, router mounting, lifespan wiring
├── database.py             # SQLAlchemy engine/session from DATABASE_URL; init_db()/drop_db()
├── models.py               # 24 ORM tables (users, listings, auctions, escrow-adjacent, esg, …)
├── conftest.py             # pytest root: in-memory SQLite TestClient fixture, staging skips
├── requirements.txt        # Python dependencies (broad; several optional)
├── runtime.txt             # python-3.11 (Render)
├── pyproject.toml          # pytest config (asyncio_mode=auto, markers, strict flags)
│
├── backend/
│   ├── api/                # 16 routers: marketplace, wallet, escrow, contracts, logistics,
│   │   │                   #   payment(+compat), trading, mineral_news, admin, notifications,
│   │   │                   #   auth, kyc (NOT mounted), ai_agents, ai_router, ai_governance,
│   │   │                   #   ai_monitoring, reliability_middleware, openapi.yaml
│   ├── websocket/          # WebSocket gateway router
│   └── (health, monitoring, security, cache, database, middleware, …)  # supporting subsystems
│
├── services/               # Business logic
│   ├── marketplace/        # ListingService (auctions, buy-it-now)
│   ├── esg/                # ESGScoringService (DB-backed metrics)
│   ├── esg_auditor.py      # Satellite-driven carbon-neutral auditor + certificate issuer
│   ├── video_negotiation.py, iot_sensor.py, ecx_compliance.py
│   ├── unified/            # GuardianAIVault, SatelliteTransactions, MicroInsuranceOracle
│   ├── sovereign/          # SovereignOnboarding
│   ├── regulatory/         # Tax oracle
│   ├── messaging/          # In-process event bus
│   ├── security/           # Quantum-shaped encryption helpers
│   └── ai-agents/          # AutonomousTradingAgent (loaded via importlib from app.py)
│
├── core/                   # Cross-cutting platform: UnifiedStateManager, SovereignAuth,
│                           #   ConflictPrevention, event_driven_architecture, health_monitor,
│                           #   reliability_system, governance_orchestrator, agent layers
│
├── tests/                  # pytest suite (unit/, api/, integration/, security/, …)
│                           #   unit/backend/test_esg_auditor.py = 34 ESG regression tests
│
├── web-client/             # React 18 + TypeScript + Vite PWA (the production frontend)
│   ├── index.html          # SPA entry (loads src/main.tsx)
│   ├── vite.config.ts      # dev proxy /api -> 127.0.0.1:8000, PWA, gzip, allowedHosts
│   ├── vercel.json         # static deploy config (worldmine.vercel.app)
│   └── src/
│       ├── app/            # App.tsx router, SessionContext, FeatureGuard (fails closed)
│       ├── design-system/  # tokens.css, shell.css, primitives, patterns, layouts
│       ├── features/       # public/ auth/ marketplace/ minerals/ workspace/ realtime/
│       ├── shared/         # api client, domain types mirrored from serializers, utils, i18n
│       └── three/          # Three.js geological environment
│
├── docs/                   # Canonical documentation (you are here)
├── .github/workflows/      # ci-cd.yml (see docs/testing.md for known gaps)
│
├── render.yaml             # Render API service definition (uvicorn, /health check)
├── Dockerfile.backend      # Multi-stage Python 3.11-slim image
├── Dockerfile.frontend     # Frontend image
├── docker-compose.dev.yml  # Local dev topology (unverified in last audit)
├── .env.example            # Environment template — placeholders only
├── cors_config.py          # Production CORS (single origin + localhost dev)
│
└── (root *.md, ai_agents/, quantum_ai_integration/, scaling/, database/, deploy/, …)
                            # Historical/research material — see docs/README.md
```

## Entry points

| Entry point | Purpose |
|---|---|
| `app.py` → `app` | The only production ASGI app (`uvicorn app:app`) |
| `web-client/index.html` | Frontend SPA entry |
| `conftest.py` | Test-time app construction (in-memory DB override) |

## Things that look like entry points but are not

- `app_simple.py`, `app_original.py` — historical variants kept for reference; **not** the deploy target.
- `start.py`, `setup.py` — legacy helpers; deployment uses `uvicorn app:app` per `render.yaml`.
- `dashboard/`, `frontend/`, `public/` (root) — earlier frontends superseded by `web-client/`.
- Most root-level `*.md` — point-in-time reports; see [README.md in this directory](README.md#historical-documents).
