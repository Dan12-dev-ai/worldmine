# Deployment

## Verified and unverified paths

| Path | Config | Verification status |
|---|---|---|
| Local (uvicorn + SQLite) | commands in [getting-started.md](getting-started.md) | **Verified** — boot + health + endpoints tested |
| Render API | `render.yaml` | **Config exists**; not deployed from this audit — treat as intent |
| Vercel frontend | `web-client/vercel.json` | Live at [worldmine.vercel.app](https://worldmine.vercel.app); config predates the Vite rebuild (`distDir: build` refers to CRA output) and likely needs updating |
| Docker | `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.dev.yml` | **Unverified** — files exist and look coherent; no build was run in this audit |

## Render (API)

`render.yaml` defines one web service:

- Build: `pip install -r requirements.txt`
- Start: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Health check: `/health` (30 s timeout), multi-region checks listed for `worldmine-api`, `worldmine-swarm`, `worldmine-payments`
- Runtime: Python 3.11; secrets (`DATABASE_URL`, `JWT_SECRET`, `REDIS_*`, …) injected as dashboard env vars (`sync: false` = "set manually, not in git")

**Operator checklist:**

1. Set `DATABASE_URL` to a managed PostgreSQL instance and run `python -c "from database import init_db; init_db()"` once against it (or enable Alembic migrations — see limitations).
2. Set a strong `JWT_SECRET` (≥32 random bytes) — the code falls back to a public placeholder.
3. Set `PRODUCTION_URL` to the exact frontend origin so CORS allows it.
4. Confirm `GET /health` returns 200 before routing traffic.
5. `/health` touches no dependencies — it is a **liveness** probe, not a readiness probe. Readiness must additionally check the database.

## Vercel (frontend)

The committed `web-client/vercel.json` predates the current build (it expects CRA's `build/` directory; the project now builds to `dist/` via Vite). Before the next frontend deploy:

- Update `distDir` (or remove it and let Vercel auto-detect the Vite output).
- Point `REACT_APP_API_URL`/`REACT_APP_WS_URL` at the real API origin (the file still references a `koyeb.app` host).
- Ensure the API's `PRODUCTION_URL` matches the final Vercel domain.

## Docker

Multi-stage `Dockerfile.backend` (python:3.11-slim, venv, build deps) and `docker-compose.dev.yml` (API + Redis topology) exist. **Not built or run in this audit** — verify locally with `docker compose -f docker-compose.dev.yml up --build` before relying on them.

## Rollback and data safety

- **No migration tooling is wired up** for production: `alembic` is in `requirements.txt` and `database/migrations/` exists, but `init_db()` (create-all) is the only mechanism exercised. Schema evolution on a live database is an unsolved operational gap.
- Frontend rollback = redeploy a previous Vercel build (platform feature).
- The in-memory stores (escrow, contracts, …) hold state that **cannot be rolled back or recovered** — another reason they must be persisted before real funds flow ([architecture.md](architecture.md#8-known-architectural-constraints-verified)).

## Operational limitations (honest list)

1. In-memory state for money-adjacent modules — not production-safe.
2. No job queue/worker topology despite Celery/Kafka libraries being installed.
3. Single-process design — no horizontal scaling story beyond running more stateless API replicas (only safe once state is externalized).
4. Health endpoint does not verify database connectivity.
5. `web-client/dist/` is committed to git — deploy artifacts and source can drift.
