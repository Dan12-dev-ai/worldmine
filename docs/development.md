# Development workflow

How to work productively in this repository without breaking the running system.

## Ground rules

1. **The code is the truth.** If a historical root-level document disagrees with the code, trust the code and update the canonical docs in `docs/`.
2. **Do not fabricate data in the UI.** The frontend's core convention (`web-client/src/features/workspace/DataPanel.tsx`) renders missing data as `—` and failures as explicit errors with retry. Preserve that pattern in new screens.
3. **Financial mutations are explicit and never auto-retried** (escrow release, contract signing, payment retries). Follow the existing pattern: no implicit writes, no auto-retry.
4. **Optional dependencies stay optional.** New integrations must be import-guarded so the app boots without them (see `app.py` optional-agent pattern).

## Day-to-day loop

```bash
# Terminal 1 — API (SQLite mode)
DATABASE_URL=sqlite:///./worldmine.db python3 -m uvicorn app:app --port 8000 --reload

# Terminal 2 — frontend
cd web-client && npm run dev          # http://localhost:5173, proxies /api -> :8000

# Terminal 3 — tests on change
python3 -m pytest tests -q
cd web-client && npx tsc --noEmit
```

## Making a change

1. Branch from `main`: `git checkout -b feature/<short-name>` (or `fix/`, `docs/`).
2. Keep changes scoped — one concern per PR. Documentation-only PRs are welcome.
3. Add or extend tests for behavioural changes (`tests/unit/`, `tests/api/`).
4. Run the full gates before opening a PR:
   - `python3 -m pytest tests` → expect **108 passed, 41 skipped** (all skips must be `staging`-marked)
   - `cd web-client && npx tsc --noEmit` → 0 errors
   - `cd web-client && npm run lint` → 0 problems
5. Open a PR with the template; describe what changed, why, and how you verified it.

## Conventions

| Area | Convention |
|---|---|
| Backend style | Existing code is mixed (snake_case everywhere, occasional emoji in logs/docstrings). Match the file you edit; do not reformat unrelated code |
| API responses | New endpoints: prefer the FastAPI-native envelope (`{"data": ..., "total": ...}`) for collections and explicit error `HTTPException`s. Do not invent a third style |
| Types | Frontend mirrors backend shapes in `web-client/src/shared/types/domain.ts` — update it when serializers change |
| Naming | In-code name is still "DEDAN Mine" in many titles; the product name is **World Mine**. Use the product name in new user-facing strings |
| Tests | Async tests use `pytest-asyncio` auto mode (`pyproject.toml`). Use the `staging` marker for anything needing live infrastructure |
| Secrets | Never hard-code; read via `os.getenv` with a safe default only for non-secrets |

## Debugging

- **Which route serves this URL?** `grep -rn "<path>" app.py backend/api/` or open `/openapi.json` (183 paths) and search.
- **500 with `no such table`** — schema missing for the `DATABASE_URL` in use ([troubleshooting.md](troubleshooting.md)).
- **Endpoint returns 503** — an optional dependency failed to import; check the guard in `app.py` and the endpoint's error body.
- **Frontend shows `—` everywhere** — the API is reachable but returning empty/absent fields; that is the honest-rendering convention, check the network response.
- **Importing a hyphenated module** (`services/ai-agents/`) — use the `importlib` pattern in `app.py` (`_load_trading_agent_cls`).

## Repository hygiene

- Do not commit `.env`, `*.db`, `node_modules/`, or `web-client/dist/` rebuilds unless the change *is* a deliberate deploy artifact (note: `web-client/dist/` is currently tracked — rebuilding it creates noisy diffs; call that out in the PR).
- Historical root-level `*.md` reports are kept for reference; do not delete them, but also do not extend them — add new material under `docs/`.
