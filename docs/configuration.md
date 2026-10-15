# Configuration reference

All configuration is environment-variable driven; `database.py` calls `load_dotenv()`, so a root `.env` is picked up automatically. Start from `.env.example` (placeholders only — never real secrets).

Variables were verified by grepping `os.getenv`/`environ.get` across the boot path (`app.py`, `backend/api/*.py`, `database.py`, `cors_config.py`). "Boot path" = code executed when the server starts.

## Core (boot path)

| Variable | Type | Purpose | Required | Default | Example |
|---|---|---|---|---|---|
| `DATABASE_URL` | URL | SQLAlchemy engine URL (PostgreSQL or SQLite) | Recommended (has fallback) | `postgresql://dedanmine:password@localhost:5432/dedanmine` | `sqlite:///./worldmine.db` |
| `JWT_SECRET` | string | HS256 key for API JWTs (`backend/api/auth.py`) | **Yes in production** | insecure placeholder `your-super-secret-jwt-key` | ≥32 random bytes |
| `PRODUCTION_URL` | URL | The one browser origin CORS allows (`cors_config.py`) | No | `https://worldmine.vercel.app` | `https://your-app.vercel.app` |
| `ENVIRONMENT` | enum | `development`/`production`; echoed by `/health` | No | `production` | `development` |
| `DEBUG` | bool | SQLAlchemy echo + verbose logging | No | `false` | `true` |
| `PORT` | int | Uvicorn port (deployment configs) | No | `8000` | `10000` |
| `HOST` | string | Uvicorn bind address | No | — | `0.0.0.0` |
| `REDIS_HOST` | string | Redis host (sessions/rate limits) | No | `localhost` | `redis` |
| `REDIS_PORT` | int | Redis port | No | `6379` | `6379` |
| `REDIS_URL` | URL | Full Redis URL (alternative to host/port) | No | — | `redis://redis:6379` |
| `SUPABASE_URL` | URL | Supabase project URL for the auth router | Auth router only | — | `https://xyz.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | secret | Server-side Supabase key for the auth router | Auth router only | — | — |
| `SENDGRID_API_KEY` | secret | Transactional email via SendGrid | Auth router only | — | `SG.…` |

> The auth router (`backend/api/auth.py`) reads `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SENDGRID_API_KEY`, `REDIS_HOST`/`REDIS_PORT`, and `JWT_SECRET` **at import time** and constructs clients immediately. If those packages/credentials are missing, mounting that router fails — it is not currently mounted by default for this reason.

## Deployment-specific (`render.yaml`)

| Variable | Purpose | Value in `render.yaml` |
|---|---|---|
| `PYTHON_VERSION` | Render Python runtime | `3.11` |
| `FASTAPI_ENV` | Framework env marker | `production` |
| `DATABASE_TYPE` | Hint for tooling | `sqlite` (set `DATABASE_URL` for PostgreSQL) |
| `CORS_ORIGINS` | Documented for operators (the code reads `PRODUCTION_URL`) | set via dashboard |
| `WORLDWIDE_OPTIMIZATION`, `EDGE_COMPUTING`, `LATENCY_TARGET`, `GLOBAL_REPLICATION` | Declared in `render.yaml`; **no consumer found in the code** — documentation-only today | — |

## Frontend (`web-client/`)

Vite loads `.env` files from `web-client/`. Both `VITE_*` and legacy `REACT_APP_*` names are exposed (see `vite.config.ts`).

| Variable | Purpose | Default |
|---|---|---|
| `VITE_API_TARGET` | Base URL the dev/preview proxy forwards `/api` to | `http://127.0.0.1:8000` |
| `REACT_APP_API_URL` | Absolute API base used by older client code (see `web-client/vercel.json`) | `https://dedan-mine-api.koyeb.app` (stale — update on deploy) |
| `REACT_APP_WS_URL` | WebSocket base for older client code | `wss://dedan-mine-api.koyeb.app` (stale) |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key for client-side auth | — |

## Integrations declared in `.env.example` only

These appear in `.env.example` and are consumed by optional services, **not** by the boot path — the app runs without them:

`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`, `CHAPA_PUBLIC_KEY`, `CHAPA_SECRET_KEY`, `CHAPA_MERCHANT_ID`, `CHAPA_WEBHOOK_URL`, Telebirr credentials, `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`, `VITE_SUPABASE_ANON_KEY`.

## Rules

1. **Never commit `.env`** — `.gitignore` excludes it; keep it that way.
2. **Set `JWT_SECRET` explicitly in production** — the fallback placeholder is public in the source.
3. **`DATABASE_URL` must be identical** for `init_db()` and the server, or you get `no such table` errors ([troubleshooting.md](troubleshooting.md)).
4. Treat any variable containing `KEY`, `SECRET`, or `PASSWORD` as a secret: inject via the platform's secret store, never inline in process listings where avoidable.

Related: [getting-started.md](getting-started.md) · [deployment.md](deployment.md) · [security.md](security.md)
