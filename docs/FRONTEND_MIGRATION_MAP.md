# FRONTEND RECONSTRUCTION — MIGRATION MAP (Phase 0 Audit)

**Rule honored:** DELETE THE UGLY UI, NOT THE PRODUCT. Nothing is deleted yet; old routes stay mounted until replacements are verified.

## BACKEND API CONTRACT MAP (MUST PRESERVE — verified from router decorators + serializers)

| Domain | Prefix | Key endpoints (verified) |
|---|---|---|
| Auth | `/api/auth` | `POST /register` (magic-link), `POST /login/magic-link`, `GET /verify`, `POST /login`, `POST /refresh`, `POST /logout`, `GET /me` |
| Marketplace | `/api/marketplace` | `GET /listings` (filters), `GET /listings/{id}`, `POST /listings`, `PUT/DELETE /listings/{id}`, `GET /auctions`, `GET /auctions/{id}`, `POST /auctions/{id}/bids`, `POST /listings/{id}/buy-now` |
| Wallet | `/api/wallet` | `GET /wallets`, `GET /wallets/{id}`, `POST /wallets`, `GET /wallets/{id}/balance`, `GET /transactions`, `POST /deposits/withdrawals/transfers` |
| Escrow | `/api/escrow` | full lifecycle: `fund|lock|milestone|release|dispute|resolve|cancel|refund`, `GET /escrow/{id}/status` |
| Contracts | `/api/contracts` | `POST /templates`, `GET /templates`, `POST /contracts` (201), `GET /contracts`, `GET /contracts/{id}`, `POST /contracts/{id}/sign`, `POST /contracts/{id}/activate` |
| Payment | `/api/payments` + compat `/api/payment` | `POST /create-payment`, `GET /payment/{id}`, `POST /create-withdrawal`, `POST /refund`, `GET /transactions`, `PUT /transactions/{id}/status`, `GET /providers`, `GET /currencies` |
| Logistics | `/api/logistics` | `POST /shipments`, `GET /shipments`, tracking by number or id, status updates, route |
| Notifications | `/api/notifications` | CRUD + read/unread + mark-all-read + preferences + unread-count + broadcast |
| AI Agents | `/api/ai_agents` | register, list/get/update/delete agents, heartbeat, assign-task, task-result, tasks |
| AI Router/Governance/Monitoring | `/api/ai-router`, `/api/ai-governance`, `/api/ai_monitoring` | router + governance + monitoring surfaces |
| Admin | `/api/admin` | dashboard stats, module health, users + role/status, audit-log, module restart, analytics, maintenance |
| KYC | `/api/kyc` | `POST /upload-document`, `POST /facial-recognition`, `GET /status/{vid}`, `GET /documents`, `POST /retry` |
| Trading | `/api/trading` | `WS /ws`, `POST /orders`, `GET /orders`, `DELETE /orders/{id}`, `GET /market-data/{mid}`, `GET /order-book/{mid}`, `GET /trades`, `GET /performance` |
| News | `/api/v2/mineral-news` | `/`, `/critical`, `/high-impact`, `/statistics`, `/categories`, `/sources`, `/search`, `/mineral/{name}`, `/trending`, `/price-impact` |

**Listing API shape (locked from `serialize_listing`):** `id, seller_id, title, description, mineral_type, quantity, unit_price, total_price, currency:"USD", quality_grade, origin, country, city, latitude, longitude, status, listing_type, created_at, updated_at`

**Escrow states (locked from `EscrowStatus`):** `created → funded → locked → pending_verification → released | disputed → resolved | cancelled | refunded` · Milestones: `payment_received, shipment_confirmed, delivery_verified, inspection_passed, final_approval`

**User model:** `user_type: miner|buyer|institutional|verifier|admin` · `verification_level: none|basic|professional|enterprise` · `tier: provisional|standard|premium|enterprise`

| Realtime | `/api/ws/{user_id}` | ConnectionManager + rooms + `/api/ws/stats` |

---

## MIGRATION MAP (OLD → NEW)

| OLD (web-client/src) | NEW | Action |
|---|---|---|
| `index.js` (CRA-style, class ErrorBoundary, console vitals) | `src/main.tsx` | REFACTOR — keep StrictMode + Sentry + boundary |
| `App.jsx` (QueryClientProvider + routes) | `src/app/App.tsx` + `app/router/*` | REFACTOR — preserve QueryClient config, Sentry/analytics, lazy routes |
| `components/AnalyticsProvider.jsx` | `src/shared/analytics/*` | PRESERVE Sentry+GA logic verbatim (security filter kept) |
| `SpatialLiquidGlassUI.jsx` (landing) | `features/public/LandingPage.tsx` | REPLACE visual, keep `/` route |
| `UniversalCheckoutUI.jsx` + `UnifiedCheckout.jsx` (`/api/payments/*`) | `features/payments/` (Phase 8) | PRESERVE logic, restyle later |
| `AgenticDashboard.jsx` (`/dashboard`) | `features/dashboard/` (Phase 6) | PRESERVE route, rebuild visual |
| `GlobalSwarmDashboard.jsx` (`/api/swarm/*`) | `features/ai/` (Phase 9) | PRESERVE — API calls kept verbatim |
| `MobileThumbZone.jsx` (`/mobile`) | `patterns/mobile-nav` | PRESERVE concept, integrate into shell |
| `PlanetaryUI.jsx` (`/api/global/stats`) | Phase 3+ | PRESERVE route |
| `PlanetaryGlobe.jsx`, `GlobalResourceMap.jsx`, `TransparencyPortal.jsx` | Phase 3/10 | PRESERVE — three.js assets reused for 3D system |
| `LocalizationDemo.jsx` | i18n hardening (Phase 1) | PRESERVE until i18n parity |
| `locales/translations.js` (en/am/es) | `src/shared/i18n/*` | PRESERVE + EXTEND |
| `reportWebVitals.js` | `shared/analytics/webVitals.ts` | PRESERVE concept |
| `index.css` (Tailwind base + dark theme) | `design-system/tokens.css` + tailwind theme | REPLACE content, keep file |
| `fetch('/api/swarm/status')` etc. | `shared/api/client.ts` wrapper | ADAPT (same URLs, typed client) |

**Route map:** `/`, `/checkout`, `/dashboard`, `/swarm`, `/planetary`, `/localization-demo`, `/mobile` all PRESERVED. NEW: `/marketplace`, `/marketplace/:listingId`, `/login`, `/register`. Catch-all `* → /` PRESERVED.

**Functionality preservation (untouched):** QueryClient (staleTime 5m / cacheTime 10m / retry 3 / exp backoff), Sentry init + beforeSend sanitizer, GA tracking functions, lazy chunking, ErrorBoundary per route, PWA plugin + manifest, manualChunks, REACT_APP_*/VITE_* env compat, esbuild JSX-in-.js loader.

## DESIGN DEBT MAP (visual layer only — to be deleted)

Cyan-on-black neon glass gradients (#00d4ff glows), glassmorphism-heavy cards, emoji-in-headings, Arial/system-font stacks with inline styles, untyped fetch without abort/timeout, placeholder GA ID fallback active, no URL-persistent filters, no systematic loading/error/empty states, no form validation layer, no route guards.

## API DRIFT FLAGS (documented, not broken — per §48)

1. `GET /api/marketplace/listings` ignores filter params server-side today → client filters + flag (adapter ready for server params).
2. `POST /api/auth/register` is magic-link based (no password) → UI copy must say "Check your email"; do not invent a password field against the contract. `/login` (password) exists for a later phase.
3. Trading WS is `/api/trading/ws` while gateway is `/api/ws/{user_id}` → two WS clients, kept separate per contract.
4. Escrow store is in-memory server-side → UI must tolerate 404-after-restart (drafts preserved client-side).
