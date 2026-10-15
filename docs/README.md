# World Mine — Documentation

Welcome to the documentation for **World Mine** (in-code name: *DEDAN Mine*), an AI-assisted mineral trading marketplace built on FastAPI and React.

New to the project? Read in this order:

1. **[Getting started](getting-started.md)** — install, configure, run, verify.
2. **[Architecture](architecture.md)** — how the system is put together.
3. **[Project structure](project-structure.md)** — what each directory and file does.

## All documents

| Document | Audience | Contents |
|---|---|---|
| [getting-started.md](getting-started.md) | Everyone | Prerequisites, install, first run, health check, common setup failures |
| [architecture.md](architecture.md) | Engineers | System context, components, request lifecycle, data flow, diagrams, constraints |
| [project-structure.md](project-structure.md) | New contributors | Verified map of the repository |
| [configuration.md](configuration.md) | Operators & devs | Every environment variable, its default, and operational effect |
| [development.md](development.md) | Contributors | Local workflow, conventions, debugging, code style |
| [testing.md](testing.md) | Contributors & maintainers | Test layout, commands, what is skipped and why, CI status |
| [deployment.md](deployment.md) | Operators | Render / Vercel / Docker paths, health checks, operational limits |
| [security.md](security.md) | Everyone | Implemented controls, secrets, boundaries, vulnerability reporting |
| [troubleshooting.md](troubleshooting.md) | Everyone | Real observed failures and their verified fixes |
| [faq.md](faq.md) | Everyone | Short answers to recurring questions |
| [glossary.md](glossary.md) | Everyone | Project-specific terms and abbreviations |
| [adr/README.md](adr/README.md) | Engineers | Architecture decision records (ADRs) |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Contributors | How to set up, branch, test, and submit changes |
| [../SECURITY.md](../SECURITY.md) | Everyone | Vulnerability reporting policy |
| [../SUPPORT.md](../SUPPORT.md) | Everyone | Where to get help |

## Historical documents

The repository root and this directory contain older audit, strategy, and report documents. They are **kept for history**; many describe plans or point-in-time audits rather than the current system. Treat them as unverified unless corroborated by the code or by the documents above.

**In `docs/`:** [QA_REPORT.md](QA_REPORT.md) (April 2026 accessibility/ISO audit), [FRONTEND_REBUILD_STATUS.md](FRONTEND_REBUILD_STATUS.md) (September 2026 frontend snapshot — largely accurate), [FRONTEND_MIGRATION_MAP.md](FRONTEND_MIGRATION_MAP.md), [LEGAL_COMPLIANCE_REPORT.md](LEGAL_COMPLIANCE_REPORT.md), [SECURE_ADMIN_WITHDRAWAL.md](SECURE_ADMIN_WITHDRAWAL.md), the three ACCEPTABILITY essays.

**In the repository root:** ~50 reports and plans (`ARCHITECTURE.md`, `COMPLETE_SYSTEM_ANALYSIS_2026.md`, `V3_*`/`V4_*`/`V6_*`, `*_SUMMARY.md`, `DATABASE_*`, `DEDAN_*` …). Several predate the current architecture; `ARCHITECTURE_AS_BUILT_AND_STRENGTH_ASSESSMENT.md` is the most self-critical of them. When a historical document conflicts with [architecture.md](architecture.md) or the code, **the code wins**.
