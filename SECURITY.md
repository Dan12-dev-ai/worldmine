# Security policy

## Reporting a vulnerability

Please **do not** report security vulnerabilities in public issues.

Use GitHub's private reporting:

1. Open the repository on GitHub.
2. **Security → Report a vulnerability** (GitHub Security Advisories).
3. Describe the issue, affected component, steps to reproduce, and impact.

You will get an acknowledgement when the maintainer sees the report. There is no dedicated security email or bug-bounty program at this time; response time is best-effort.

For non-exploitable bugs (hardening ideas, dependency updates, documentation gaps), a normal issue is fine.

## Supported versions

This project has no formal release train. The only supported version is the latest commit on `main`. Fixes are applied at the maintainer's discretion.

## Security-relevant design notes

Read [docs/security.md](docs/security.md) for the full inventory. Summary of current posture:

- JWT auth (HS256) with `JWT_SECRET` from the environment — **the built-in fallback is a public placeholder; production deployments must set it**.
- CORS is restricted to `PRODUCTION_URL` plus localhost development origins.
- Secrets belong in `.env` (git-ignored) or the platform secret store — never in code, logs, or issues.
- KYC document verification is currently **not mounted** (OpenCV dependency) — do not represent it as active.
- Sovereign-auth endpoints (`/api/v4/auth/*`, `/api/v4/sovereign/*`) currently return **mock verifications** and must not be trusted as real authentication.
- Escrow/contracts state is in-memory only — not suitable for real funds.

## Dependency hygiene

`requirements.txt` is broad; not every listed package is exercised by the running app. Review and prune carefully, and run `npm audit` inside `web-client/` when touching frontend dependencies.
