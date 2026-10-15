# Getting started

This guide takes a fresh checkout to a running API and frontend on a developer machine. Every command was executed on Linux with Python 3.11+ and Node 18+.

## Prerequisites

| Requirement | Needed for | Notes |
|---|---|---|
| Python 3.11+ | Backend | `runtime.txt` pins `python-3.11` for deployment |
| Node.js 18+ and npm | Frontend | Vite 4 toolchain |
| PostgreSQL 14+ | *Optional* — production-grade persistence | Not required for local dev; SQLite works |
| Redis | *Optional* — sessions, rate limiting | App boots without it |
| Git | Everything | — |

No Docker required. No API keys are required for the zero-dependency mode below.

## 1. Get the code and install the backend

```bash
git clone https://github.com/Dan12-dev-ai/worldmine.git
cd worldmine

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` is broad (AI SDKs, Selenium, Kafka client, WebAuthn, liboqs…). A few entries (`opencv-python`, `liboqs-python`) may fail to build on some platforms. **They are not needed for this guide** — comment them out and retry; the app import-guards optional dependencies.

## 2. Configure the environment

```bash
cp .env.example .env
```

For the zero-dependency run you can leave `.env` empty and pass variables inline (what the commands below do). At minimum, set `DATABASE_URL`. Never commit `.env`; see [configuration.md](configuration.md) for every variable.

## 3. Create the database schema

```bash
DATABASE_URL=sqlite:///./worldmine.db python3 -c "from database import init_db; init_db()"
```

This creates 24 tables (`users`, `listings`, `auctions`, `bids`, `escrow`-adjacent tables, `esg_metrics`, …) in `worldmine.db`.

> Skipping this step is the #1 first-run failure: the server still boots, but any endpoint that touches a table returns `500 no such table: listings`. See [troubleshooting.md](troubleshooting.md).

## 4. Start the API

```bash
DATABASE_URL=sqlite:///./worldmine.db python3 -m uvicorn app:app --host 127.0.0.1 --port 8000
```

## 5. Verify

```bash
curl -s http://127.0.0.1:8000/health
# {"status":"healthy","timestamp":...,"version":"2.0.0","service":"dedan-mine-api",...}

curl -s http://127.0.0.1:8000/api/marketplace/listings
# {"data":[],"total":0,"page":1,"page_size":20,"has_next":false,"has_previous":false}

curl -s -X POST http://127.0.0.1:8000/api/v4/esg/calculate-carbon-neutral-score \
  -H 'Content-Type: application/json' \
  -d '{"listing_data":{"listing_id":"demo-1","mineral_type":"gold","location":{"latitude":9.0,"longitude":38.0}}}'
# {"success":true,"listing_id":"demo-1","esg_score":{...},"satellite_data":{...}}
```

Interactive docs: <http://127.0.0.1:8000/docs> (Swagger UI) and `/redoc`.

## 6. Start the frontend (optional)

```bash
cd web-client
npm install
npm run dev
```

Vite serves <http://localhost:5173> and proxies `/api` to `http://127.0.0.1:8000` (override with `VITE_API_TARGET`). Build and preview a production bundle with `npm run build && npx vite preview --port 4173`.

## 7. Run the tests (optional)

```bash
python3 -m pytest tests        # expect: 108 passed, 41 skipped
```

## Using PostgreSQL instead of SQLite

```bash
createdb worldmine
DATABASE_URL=postgresql://user:pass@localhost:5432/worldmine python3 -c "from database import init_db; init_db()"
DATABASE_URL=postgresql://user:pass@localhost:5432/worldmine python3 -m uvicorn app:app --port 8000
```

## Common setup failures

| Symptom | Cause | Fix |
|---|---|---|
| `500` + `no such table: …` | Server and `init_db()` used different `DATABASE_URL`s, or `init_db()` never ran | Re-run `init_db()` with the same URL the server uses |
| `ModuleNotFoundError: cv2` at import | Trying to mount the KYC router | It is intentionally not mounted; see the comment in `app.py` |
| `ModuleNotFoundError: sendgrid` / `supabase` | Partial `pip install` | Re-run `pip install -r requirements.txt`, or accept that the auth router will be degraded |
| Marketplace returns empty lists | Fresh database | Expected; seed listings or use the API to create them |
| Port already in use | Another process on :8000 | `--port 8001` and point the frontend proxy at it |

Next: [architecture.md](architecture.md) · [configuration.md](configuration.md) · [troubleshooting.md](troubleshooting.md)
