# Contributing to World Mine

Thanks for helping improve the platform. This guide keeps contributions reviewable and safe.

## Before you start

- Read [docs/getting-started.md](docs/getting-started.md) to get a running instance.
- Skim [docs/architecture.md](docs/architecture.md) and [docs/development.md](docs/development.md).
- Search existing issues/PRs before opening a new one.

## Development setup

```bash
git clone https://github.com/Dan12-dev-ai/worldmine.git
cd worldmine
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DATABASE_URL=sqlite:///./worldmine.db python3 -c "from database import init_db; init_db()"
DATABASE_URL=sqlite:///./worldmine.db python3 -m uvicorn app:app --port 8000   # terminal 1
cd web-client && npm install && npm run dev                                    # terminal 2
```

## Workflow

1. **Fork** and create a feature branch from `main`:
   - `feature/<short-name>` — new capability
   - `fix/<short-name>` — bug fix
   - `docs/<short-name>` — documentation only
2. **Make the change**, scoped to one concern. Do not reformat or refactor unrelated code in the same PR.
3. **Add/extend tests** for behavioural changes; documentation changes need no tests but must keep links valid.
4. **Run the gates** (all must pass locally):

   ```bash
   python3 -m pytest tests                 # expect: 108 passed, 41 skipped
   cd web-client && npx tsc --noEmit      # expect: 0 errors
   cd web-client && npm run lint           # expect: 0 problems
   ```

5. **Commit** with a clear message (conventional-commit style preferred: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
6. **Open a PR** using the template. Explain *what* changed, *why*, and *how you verified it*. If CI is red for reasons unrelated to your change, say so.

## Contribution rules

- **No fabricated data.** The project's honesty convention (missing → `—`, failure → explicit error) applies to docs too. Do not claim features, benchmarks, or integrations that do not exist.
- **No secrets.** Never commit `.env`, keys, tokens, or real user data. See [SECURITY.md](SECURITY.md).
- **Keep the app bootable.** Optional integrations must be import-guarded ([docs/adr/0002](docs/adr/0002-import-guarded-optional-dependencies.md)).
- **Financial mutations stay explicit.** No auto-retry or implicit writes for escrow/contract/payment actions.
- **Preserve attribution.** Do not remove existing authorship or add license terms (none is chosen yet).
- **Docs live in `docs/`.** Do not extend the historical root-level reports; update the canonical docs.

## Reporting bugs

Use the **Bug report** issue template. Include: exact command, full traceback/log, OS + Python/Node versions, and whether you modified anything. For security issues **do not file a public issue** — follow [SECURITY.md](SECURITY.md).

## Proposing features

Use the **Feature request** template. Large features should start as a discussion/issue for design alignment before a PR.

## Review expectations

- Maintainers review for correctness, honesty of documentation, test coverage, and scope.
- PRs that weaken tests, security controls, or the honesty conventions will not be merged.
- All checks in the PR template must be honestly ticked.

## Licensing note

This repository currently has **no license**. By contributing, you agree your contribution may be distributed under whatever license the owner later selects (you retain copyright). If that is unacceptable, say so in the PR before investing significant work.
