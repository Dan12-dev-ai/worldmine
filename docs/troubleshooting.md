# Troubleshooting

Every entry below was **observed** during verification of this repository, not guessed.

## 500 + `no such table: listings`

**Observed:** `GET /api/marketplace/listings` returns 500; log shows `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: listings`.

**Cause:** The schema was never created, or `init_db()` ran against a *different* `DATABASE_URL` than the server uses (each SQLite URL is a separate file).

**Fix:**

```bash
# Use the SAME URL for both commands
export DATABASE_URL=sqlite:///./worldmine.db
python3 -c "from database import init_db; init_db()"
python3 -m uvicorn app:app --port 8000
```

## `ModuleNotFoundError: No module named 'cv2'`

**Observed:** importing `backend.api.kyc` fails; OpenCV is absent.

**Context:** This is why the KYC router is **intentionally not mounted** — see the comment above the router imports in `app.py`. If you need KYC: `pip install opencv-python-headless`, then mount the router. Otherwise ignore.

## `ModuleNotFoundError: No module named 'sendgrid'` (or `supabase`, `webauthn`, `oqs`)

**Cause:** Partial install of the broad `requirements.txt`, or optional dependencies unavailable on your platform.

**Effect:** The app still boots (imports are guarded); auth-router and sovereign-auth endpoints degrade or 503. Re-run `pip install -r requirements.txt`, or comment out the packages you do not need.

## Frontend build fails on `tsc`

Run `cd web-client && npx tsc --noEmit` and read the first errors — they cascade. If the tree is clean, ensure your Node is 18+ and `npm install` completed (`node_modules` present).

## Vite dev server: 403 on a tunnel/custom hostname

**Cause:** Vite's host allow-listing. **Fix (already in repo):** `web-client/vite.config.ts` sets `allowedHosts: true` for preview; tighten for production exposure.

## Marketplace works locally but returns 500 in deployment

Almost always the database: the platform's `DATABASE_URL` points at an uninitialized PostgreSQL database. Run `init_db()` against it once ([deployment.md](deployment.md)).

## ESG endpoint returns `{"success": false, ...}`

The inline handler swallows exceptions. Check the API log for the traceback; common causes are malformed `listing_data` (missing `listing_id`, `mineral_type`, or `location`) — the happy path is in [getting-started.md](getting-started.md#5-verify).

## Trading returns `[]` / news returns empty

Not an error. Trading serves seeded/mocked rows with placeholder auth; news aggregation needs provider API keys. The frontend labels these states honestly — do not mistake empty arrays for failures.

## `Address already in use` on :8000

Another process holds the port: `ss -ltnp | grep 8000` then either stop it or start on another port and set `VITE_API_TARGET` accordingly.

## Tests fail with `staging` skips you expected to run

Integration/performance tests are skipped unless `RUN_STAGING_TESTS=1` **and** a live environment exists. That is by design ([testing.md](testing.md)).

## Still stuck?

Check `/tmp`-free diagnostics first: the uvicorn log, `curl -s localhost:8000/health`, and `python3 -c "import app"`. For anything reproducible, open a bug report with the exact command, full traceback, and environment (Python/Node versions, OS) — see [../CONTRIBUTING.md](../CONTRIBUTING.md).
