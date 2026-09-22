# World Mine — Frontend Rebuild: Status & Verification Report

_Last verified: 2026-09-22 (typecheck, lint, production build, and live end-to-end checks)._

## 1. What this document is

A single, honest snapshot of the frontend rebuild: what is finished, what is
wired to real endpoints, which parts are degraded and **why**, and how to run and
verify each layer. Every claim below was produced by running the code, not by
reading intent from the source.

---

## 2. Gate results (all run just now)

| Gate | Command | Result |
| --- | --- | --- |
| Typecheck | `npx tsc --noEmit` | **0 errors** |
| Lint | `npx eslint src --ext .ts,.tsx` | **0 problems** |
| Production build | `npm run build` (tsc && vite build) | **✓ built in 38.39s**, 2739 modules, PWA service worker generated |
| Code splitting | build output | 1 vendor chunk + one chunk per workspace module (DealsPage, ContractsPage, EscrowPage, LogisticsPage, MessagesPage, ProfilePage, SecurityPage, AdminPage, NewsPage, ContentPages) |
| Runtime smoke test | `vite preview` on :4173 | `/` 200, `/marketplace` 200, `/login` 200, deep links 200 |
| API proxy | `curl localhost:4173/api/admin/dashboard/stats` | **200 + live JSON** |

---

## 3. Architecture

```
web-client/src/
├── main.tsx                     # TS entry (index.html repointed from index.js)
├── app/
│   ├── App.tsx                  # router: public / auth / user / admin + legacy routes
│   ├── legacy/index.ts          # typed seam for preserved JSX screens (@ts-expect-error isolated here)
│   ├── providers/SessionContext.tsx
│   └── router/FeatureGuard.tsx  # fails closed; server stays authoritative
├── design-system/               # tokens.css, components.css, shell.css
│   ├── primitives/              # WorldButton, WorldBadge, WorldStatus, skeletons, states
│   ├── patterns/                # MineralCard, VerificationBadge, EscrowTimeline, ProvenanceTimeline, LifecycleStepper
│   └── layouts/                 # AppShell, WorldHeader, WorldFooter
├── features/
│   ├── public/                  # LandingPage, NewsPage, ContentPages (how-it-works, traceability, compliance, esg, support)
│   ├── auth/                    # LoginPage, RegisterPage (magic-link, 4 steps)
│   ├── marketplace/             # MarketplacePage (URL-persistent filters, grid+list, facets, save-search)
│   ├── minerals/                # MineralDetailPage (verification, specs, sticky seller panel)
│   ├── workspace/               # ModuleFrame, DataPanel, useResource + 8 modules
│   └── realtime/                # RealtimeProvider
└── shared/
    ├── api/client.ts            # typed fetch, ApiError, credentials: 'include'
    ├── api/defaultQueryFn.ts    # string query keys -> typed client (GET only)
    ├── types/domain.ts          # every shape mirrored from backend serializers
    ├── utils/format.ts          # honest formatters (absent -> "—", never invented)
    └── i18n/                    # legacy translations imported directly
```

### Design rules enforced throughout

1. **No fabricated data.** A missing field renders `—` or an explicit statement.
   A failed request renders an error with a retry, never an empty table.
2. **Loading / error / empty / wrong-shape are four distinct states** — handled in
   one place (`workspace/DataPanel.tsx`) so no module can blur them.
3. **Financial and legal mutations are never implicit and never auto-retried.**
   Escrow release/dispute, contract signing and payment retries are deliberately
   not wired to buttons.
4. **Contracts are mirrored, not reinterpreted.** Types in `shared/types/domain.ts`
   carry the endpoint they came from.
5. **Legacy routes preserved verbatim:** `/checkout`, `/swarm`, `/planetary`,
   `/localization-demo`, `/mobile`, plus `/dashboard` → `/swarm` and catch-all → home.

---

## 4. Route inventory

| Route | Screen | Backing data | Status |
| --- | --- | --- | --- |
| `/` | LandingPage | static + listing preview | live |
| `/marketplace` | MarketplacePage | `GET /api/marketplace/listings` | **degraded** — endpoint 500s without PostgreSQL (see §6.6) |
| `/marketplace/:id` | MineralDetailPage | `GET /api/marketplace/listings/{id}` | degraded (same cause) |
| `/login` `/register` | auth | `/api/auth/*` | live (magic-link contract) |
| `/deals` | DealsPage | `/api/trading/orders`, `/trades`, `/performance` | live (mounted this pass) |
| `/contracts` | ContractsPage | `/api/contracts/contracts`, `/templates` | live |
| `/escrow` | EscrowPage | `GET /api/escrow/escrow` (+ server-side `?status=`) | live |
| `/logistics` | LogisticsPage | `/api/logistics/shipments`, `/track/{n}` | live |
| `/messages` | MessagesPage | `/api/notifications/notifications?user_id=` + mark-all-read | live |
| `/profile` | ProfilePage | `/api/auth/me`, `/api/kyc/documents` | partly live — KYC router unmounted (see §6.3) |
| `/security` | SecurityPage | capability report | live (states missing controls explicitly) |
| `/admin` | AdminPage | `/api/admin/dashboard/stats`, `/modules/health`, `/audit-log` | live but stats are seeded (§6.4) |
| `/news` | NewsPage | `/api/v2/mineral-news/*` | live (mounted this pass; returns `[]` legitimately) |
| `/how-it-works` `/traceability` `/compliance` `/esg` `/support` | content pages | static, real copy | live |
| `/checkout` `/swarm` `/planetary` `/localization-demo` `/mobile` | legacy JSX | unchanged | preserved |

---

## 5. Backend contract findings (verified by reading the routers and curling them)

### 5.1 Routers that existed but were never mounted — FIXED
`backend/app.py` mounted marketplace, wallet, escrow, ai_*, payment, contracts,
logistics, notifications, admin and the websocket gateway. **Trading and
mineral-news were never mounted**, so `/api/trading/*` and `/api/v2/mineral-news/*`
returned 404 to the frontend. Both import cleanly and are now mounted:

```python
app.include_router(trading_router)
app.include_router(mineral_news_router)
```

Verified after mounting: `/api/trading/orders` 200, `/api/trading/performance` 200,
`/api/v2/mineral-news/?limit=2` 200.

### 5.2 Escrow list returns an envelope, not an array
`GET /api/escrow/escrow` responds `{"data": [...]}`. A client that assumes a bare
array silently shows "no escrows". `useResourceList` normalises **both** shapes and
reports anything else as a contract break.

### 5.3 KYC router cannot be mounted
`backend/api/kyc.py` imports `cv2` (OpenCV) for facial recognition, which is not
installed in this environment. The router is left unmounted and documented rather
than half-wired. Consequence: `/api/kyc/documents` 404s and ProfilePage's document
panel shows its error state.

### 5.4 Admin telemetry is seeded, not measured
`/api/admin/dashboard/stats` returns a hard-coded statistics record, and
`/api/admin/modules/health` returns a fixed `healthy` / `uptime 86400` /
`error_rate 0.01` for **every** module. AdminPage displays them **and labels them
as seeded placeholders** so nobody mistakes them for live telemetry.

### 5.5 In-memory stores (data does not survive restart)
escrow, logistics, notifications and admin keep state in module-level dicts
(`# In-memory storage`). The corresponding screens say so in their descriptions.
Trading additionally serves seeded/mock rows and authenticates with a placeholder
dependency (`Depends(lambda: {"user_id": "test_user"})`), **not** a verified JWT —
DealsPage states this rather than presenting the rows as verified history.

### 5.6 PostgreSQL is required by marketplace (and is not running here)
`GET /api/marketplace/listings` raises `psycopg2.OperationalError: connection to
server at "localhost", port 5432 failed: Connection refused`. This is a backend
dependency, not a frontend defect: the marketplace screens show their honest error
state with a retry. Start PostgreSQL and seed listings to make them live.

### 5.7 Enums captured exactly (no guessing)
`ContractStatus` (draft, pending_signature, signed, active, expired, terminated),
`ContractType`, `EscrowStatus`, `EscrowMilestone`, `ShipmentStatus`, `TransportMode`,
`NotificationType/Channel/Priority`, `SystemModuleName` — all read from the backend
enums into `shared/types/domain.ts`.

### 5.8 Session identity drift
`GET /api/auth/me` serializes `UserResponse` (first/last name, kyc_status, kyc_level,
is_verified, created_at, last_login) and exposes **no role field**. The session type
was corrected to `SessionUser` and role gating **fails closed**: the header shows
first name + verification state (not `username`/`verification_level`, which that
endpoint never sends), and `/admin` stays unreachable until the endpoint returns a
role claim.


---

## 6. How to run and verify

```bash
# 1. API (from the repo root)
python3 -m uvicorn app:app --host 127.0.0.1 --port 8000

# 2. Frontend dependencies + production build
cd web-client
npm install
npm run build            # tsc && vite build

# 3. Serve the production build (proxies /api to :8000)
npx vite preview --port 4173 --strictPort
```

`vite.config.ts` → `preview.proxy` forwards `/api` (and websockets) to
`http://127.0.0.1:8000`, so the built app talks to the API on the same origin.
Override with `VITE_API_TARGET` when the API lives elsewhere. Tunnel hostnames are
allowed via `preview.allowedHosts` so a public review link works.

---

## 7. Known limitations (stated, not hidden)

1. **Marketplace + mineral detail need PostgreSQL** (§5.6).
2. **KYC document panel** needs the cv2 dependency before the router can mount (§5.3).
3. **Admin analytics are seeded** (§5.4); module health measures nothing yet.
4. **No MFA, session inventory, recovery codes or ticket system** — SecurityPage and
   SupportPage state the missing capability instead of showing inert controls.
5. **Deal-room chat, video and documents** are not built; DealsPage presents orders,
   trades and performance only.
6. **Marketplace filters** are applied client-side while still being sent as query
   params, because the backend ignores them today (adapter-ready).
7. **The public review tunnel is temporary** (60-minute free tier per session).

---

## 8. Recommended next steps

1. Point the marketplace serializer at a real database and seed listings.
2. Mount the KYC router (install `opencv-python-headless`) or remove the cv2 import.
3. Replace the seeded admin stats and module health with measured values.
4. Replace in-memory stores with persisted models before any real money moves.
5. Give `/api/auth/me` a role claim, then verify the admin gate end-to-end.
6. Then resume product phases: deal-room negotiation, chat and document exchange.

