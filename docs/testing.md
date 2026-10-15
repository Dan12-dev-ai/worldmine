# Testing

## Framework and layout

| Suite | Location | Framework | Notes |
|---|---|---|---|
| Backend unit + integration | `tests/` (18 subdirs: `unit/`, `api/`, `integration/`, `security/`, `blockchain/`, `monitoring/`, `performance/`, `e2e/`, …) | pytest (+ `pytest-asyncio` auto mode, `httpx` TestClient) | Root `conftest.py` supplies an in-memory SQLite `client` fixture |
| Frontend | none (no unit-test runner configured) | — | Verification = `tsc --noEmit` + `eslint` + production build |
| ESG regression | `tests/unit/backend/test_esg_auditor.py` | pytest (async) | 34 tests pinning carbon-neutral scoring, thresholds, certificates, audit trail |

## Commands (all verified)

```bash
python3 -m pytest tests                     # full backend suite
python3 -m pytest tests/unit/backend/test_esg_auditor.py   # ESG module only
python3 -m pytest tests -q -k marketplace   # filter by name

cd web-client
npx tsc --noEmit                            # typecheck (0 errors)
npm run lint                                # eslint, --max-warnings 0
npm run build                               # tsc && vite build (production)
```

**Last verified full-suite result:** `108 passed, 41 skipped` (exit 0). All 41 skips carry the `staging` marker.

## How the hermetic test database works

`conftest.py` (repository root):

1. Sets `DATABASE_URL=sqlite:///./test_worldmine.db` *before* importing `database` (import-time engine creation).
2. Builds a separate in-memory SQLite engine with `StaticPool`, creates all `models.Base` tables.
3. Overrides the FastAPI `get_db` dependency, and yields a session-scoped `TestClient`.

Consequence: API tests never touch your dev database and never need PostgreSQL. Tests that genuinely need live infrastructure are marked `staging` and **skipped unless `RUN_STAGING_TESTS=1`**:

```bash
RUN_STAGING_TESTS=1 python3 -m pytest tests/integration   # requires deployed env
```

## Configuration details (`pyproject.toml`)

- `asyncio_mode = "auto"` — plain `async def test_...` works, no decorators.
- `--strict-markers --strict-config` — unknown markers fail the run (good).
- `filterwarnings = ["error"]` (with common deprecation warnings ignored) — warnings surface as failures.
- Markers defined: `redis`, `blockchain`, `quantum`, `security`, `performance`, `load`, `chaos`, `staging`.

## CI status — known gaps (verified, not speculation)

`.github/workflows/ci-cd.yml` exists and defines jobs (`quality-check`, `test-suite`, …) but **does not match the repository tree**:

| Gap | Evidence | Consequence |
|---|---|---|
| Runs `npm ci` at repo root | Workflow has no `working-directory`; root has **no `package.json`** | Frontend jobs fail immediately |
| References `npm run test:coverage` | No such script in `web-client/package.json` | Even with correct cwd, the coverage step fails |
| No backend pytest job | Workflow only configures Node | Python suite (108 tests) is never run in CI |
| Node version pinned to 16/18/20 matrix | Frontend toolchain is Vite 4 / TS 5 | Node 16 is below Vite 4's supported range |
| Uses deprecated `::set-output` | Workflow body | GitHub has deprecated this command |

**Proposed fix (not yet applied — changes to CI need maintainer review):** add `defaults: run: working-directory: web-client` to the Node jobs, replace the coverage step with `npm run build`, and add a Python job (`actions/setup-python@v5` with 3.11 → `pip install -r requirements.txt` → `python -m pytest tests`). Until then, treat local test runs as the only gate.

## Known test-coverage gaps

1. **No frontend unit tests** — component behaviour is verified manually and via typecheck.
2. **In-memory-store modules** (escrow, contracts, logistics, notifications, admin) have endpoint tests only where state shape is asserted; durability is untested because persistence does not exist yet.
3. **Auth router** (`backend/api/auth.py`) — not covered; requires Supabase/Redis/SendGrid.
4. **Sovereign-auth endpoints** return mock verifications; tests assert the mock, not real protocol flows.
5. **Performance/staging tests exist but are skipped** by default (`performance/`, `integration/test_load_scenarios.py`).
