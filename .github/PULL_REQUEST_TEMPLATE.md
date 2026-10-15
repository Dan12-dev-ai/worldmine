<!-- Thank you for contributing. Please complete every section honestly. -->

## What changed

<!-- Describe the change and the problem it solves. Link related issues: "Fixes #123". -->

## Why

<!-- Motivation, context, trade-offs considered. -->

## How it was verified

<!-- Commands run, endpoints hit, screenshots. Be specific: "pytest tests → 108 passed, 41 skipped". -->

## Checklist

- [ ] `python3 -m pytest tests` passes locally (no new failures)
- [ ] `cd web-client && npx tsc --noEmit` passes (if frontend touched)
- [ ] `cd web-client && npm run lint` passes (if frontend touched)
- [ ] New/changed behaviour has tests or a stated reason why not
- [ ] Documentation updated (`docs/` — not the historical root-level reports)
- [ ] No secrets, `.env` files, or real user data included
- [ ] No unrelated files reformatted or moved
- [ ] Financial/irreversible actions remain explicit and non-auto-retried
- [ ] Claims in docs/UI are verifiable — no fabricated data, benchmarks, or integrations

## Notes for reviewers

<!-- Risk areas, follow-ups, anything you deliberately left out. -->
