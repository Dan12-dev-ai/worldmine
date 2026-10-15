# Security

## Reporting a vulnerability

Use **GitHub Security Advisories → Report a vulnerability** on this repository (private disclosure to the maintainer). Do **not** open a public issue for exploitable vulnerabilities. There is no dedicated security email on file; if you are a researcher and cannot use advisories, open a public issue asking for a contact **without** including exploit details.

## Implemented controls (verified in code)

| Control | Where | Notes |
|---|---|---|
| CORS allow-list | `cors_config.py`, `app.py` | Single production origin (`PRODUCTION_URL`) + localhost dev origins; credentials allowed only for allow-listed origins |
| JWT bearer auth | `backend/api/auth.py` | HS256, 24 h expiry, `HTTPBearer` extraction |
| Password hashing | `bcrypt` in `backend/api/auth.py` | — |
| Secret handling | `.env` excluded by `.gitignore`; `.env.example` contains placeholders only | Verified: no real secrets in tracked files |
| Dependency hygiene | `requirements.txt` pinned loosely (>=); pre-commit config exists (`.pre-commit-config.yaml`) | — |
| Database row-level security policies | `database/rls_policies.py` | Defined for PostgreSQL RLS |
| Frontend gating | `web-client/src/app/router/FeatureGuard.tsx` | **Fails closed**; server remains authoritative for authorization |
| Input validation | Pydantic request models across routers | — |
| TrustedHost + GZip middleware | `app.py` | — |

## Known security concerns (confirmed, in priority order)

1. **`JWT_SECRET` fallback** — `backend/api/auth.py` defaults to the literal string `your-super-secret-jwt-key`, which is public in the source. Any deployment that forgets to set `JWT_SECRET` issues forgeable tokens. *Fix: fail fast at boot when `ENVIRONMENT=production` and the secret is unset/placeholder.*
2. **Money-adjacent state in memory** — escrow/contracts live in module dicts with no durable audit trail; a restart silently destroys records. No direct exploit, but a data-integrity hazard for anything resembling real value.
3. **Mock authentication endpoints** — `/api/v4/auth/{fido2,ssi,pqc,zk,behavioral,liveness}/verify` and `/api/v4/sovereign/*` accept payloads and return success-shaped mock results (`webauthn` and `liboqs` are not even installed). If any client trusts these responses as real verification, that trust is misplaced. *Recommendation: mark them `experimental` in the OpenAPI schema or return 501 until implemented.*
4. **KYC router unmounted** — document verification does not run; do not represent listings as KYC-verified in product copy.
5. **Auth router constructs Supabase client with the service-role key at import** — service-role bypasses RLS; this module must never be exposed to untrusted code paths.
6. **No rate limiting verified** — `reliability_middleware.py` exists but per-route rate-limit policy was not exercised in this audit.
7. **Broad dependency surface** — `requirements.txt` includes Selenium, Kafka client, Elasticsearch, and crypto libraries that the running app does not use; every unused dependency is supply-chain exposure. *Recommendation: split into `requirements.txt` (core) + `requirements-optional.txt`.*

## Secrets management rules

- Never commit `.env`; never paste keys into issues, PRs, logs, or screenshots.
- Inject secrets via the platform secret store (Render dashboard env vars in the current setup).
- Rotate `JWT_SECRET`, Supabase keys, and SendGrid keys on any suspected exposure; rotating `JWT_SECRET` invalidates all outstanding tokens.
- Frontend bundles are public: only `VITE_*`/`REACT_APP_*` values belong there, and only **anon** (never service-role) keys.

## Permission model

Authorization currently rests on: JWT validity (auth router, when mounted) and the frontend's fail-closed `FeatureGuard`. The `/api/auth/me` response exposes **no role claim**, so admin gating cannot be enforced end-to-end yet — a known gap tracked in the README roadmap. Treat all `/api/admin/*` endpoints as requiring server-side authorization work before public exposure.
