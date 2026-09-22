/**
 * World Mine — Application root (reconstructed, contract-preserving).
 *
 * PRESERVED from legacy App.jsx: QueryClientProvider (staleTime 5m, retry 3,
 * exp backoff), lazy chunks, catch-all → home redirect, Suspense fallback.
 *
 * NEW (Phase 2–5): domain router (public/auth/marketplace/user/admin), app
 * shell with global navigation, FeatureGuard route protection, session refetch
 * on focus, SessionProvider, i18n, error boundary.
 *
 * Legacy routes stay mounted and untouched (migration map): /checkout,
 * /dashboard(redirect), /swarm, /planetary, /localization-demo, /mobile.
 */
import { Suspense, lazy, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider, useQueryClient } from 'react-query';
import { useTranslation } from 'react-i18next';

import '../shared/i18n'; // side-effect: i18n init (legacy wiring lived in App.jsx)
import { SessionProvider } from './providers/SessionContext';
import { defaultQueryFn } from '../shared/api/defaultQueryFn';
import { ErrorBoundary } from '../shared/components/ErrorBoundary';
import { AppShell } from '../design-system';
import { FeatureGuard } from './router/FeatureGuard';


/* ---------- Legacy routes (preserved verbatim, typed via app/legacy shim) ---------- */
const PlanetaryUI = lazy(() => import('../app/legacy').then((m) => ({ default: m.PlanetaryUI })));
const GlobalSwarmDashboard = lazy(() => import('../app/legacy').then((m) => ({ default: m.GlobalSwarmDashboard })));
const UnifiedCheckoutUI = lazy(() => import('../app/legacy').then((m) => ({ default: m.UniversalCheckoutUI })));
const MobileThumbZone = lazy(() => import('../app/legacy').then((m) => ({ default: m.MobileThumbZone })));
const LocalizationDemo = lazy(() => import('../app/legacy').then((m) => ({ default: m.LocalizationDemo })));

/* ---------- New domain pages ---------- */
const LandingPage = lazy(() => import('../features/public/LandingPage').then((m) => ({ default: m.LandingPage })));
const MarketplacePage = lazy(() => import('../features/marketplace/MarketplacePage').then((m) => ({ default: m.MarketplacePage })));
const MineralDetailPage = lazy(() => import('../features/minerals/MineralDetailPage').then((m) => ({ default: m.MineralDetailPage })));
const LoginPage = lazy(() => import('../features/auth/LoginPage').then((m) => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('../features/auth/RegisterPage').then((m) => ({ default: m.RegisterPage })));

/* ---------- Workspace modules (Phase 6–9) — each reads real endpoints ---------- */
const DealsPage = lazy(() => import('../features/workspace/deals/DealsPage').then((m) => ({ default: m.DealsPage })));
const ContractsPage = lazy(() => import('../features/workspace/contracts/ContractsPage').then((m) => ({ default: m.ContractsPage })));
const EscrowPage = lazy(() => import('../features/workspace/escrow/EscrowPage').then((m) => ({ default: m.EscrowPage })));
const LogisticsPage = lazy(() => import('../features/workspace/logistics/LogisticsPage').then((m) => ({ default: m.LogisticsPage })));
const MessagesPage = lazy(() => import('../features/workspace/messages/MessagesPage').then((m) => ({ default: m.MessagesPage })));
const ProfilePage = lazy(() => import('../features/workspace/profile/ProfilePage').then((m) => ({ default: m.ProfilePage })));
const SecurityPage = lazy(() => import('../features/workspace/security/SecurityPage').then((m) => ({ default: m.SecurityPage })));
const AdminPage = lazy(() => import('../features/workspace/admin/AdminPage').then((m) => ({ default: m.AdminPage })));

/* ---------- Public content + intelligence pages ---------- */
const NewsPage = lazy(() => import('../features/public/NewsPage').then((m) => ({ default: m.NewsPage })));
const HowItWorksPage = lazy(() => import('../features/public/ContentPages').then((m) => ({ default: m.HowItWorksPage })));
const TraceabilityPage = lazy(() => import('../features/public/ContentPages').then((m) => ({ default: m.TraceabilityPage })));
const CompliancePage = lazy(() => import('../features/public/ContentPages').then((m) => ({ default: m.CompliancePage })));
const EsgPage = lazy(() => import('../features/public/ContentPages').then((m) => ({ default: m.EsgPage })));
const SupportPage = lazy(() => import('../features/public/ContentPages').then((m) => ({ default: m.SupportPage })));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // PRESERVED: legacy cache behavior
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      retry: 3,
      retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 30000),
      // NEW: queryFn resolves paths straight to the API client (same URLs)
      queryFn: defaultQueryFn,
    },
  },
});

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <SessionProvider>
          <BrowserRouter>
            <Suspense fallback={<LazyFallback />}>
              <SessionRefresher />
              <RouteAnalytics />
              <AppRoutes />
            </Suspense>
          </BrowserRouter>
        </SessionProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

function LazyFallback() {
  return (
    <div className="wm-container" style={{ padding: 'var(--space-9) var(--gutter)' }} role="status" aria-live="polite">
      <div className="wm-skeleton" style={{ height: 320 }} />
      <p className="wm-sr-only">Loading…</p>
    </div>
  );
}

/* Session lifecycle: refetch on focus + 15-min interval (timeout handling, §14). */
function SessionRefresher() {
  const queryClient = useQueryClient();
  useEffect(() => {
    const onFocus = () => {
      if (document.visibilityState === 'visible') {
        queryClient.invalidateQueries('session');
      }
    };
    window.addEventListener('focus', onFocus);
    const id = window.setInterval(() => queryClient.invalidateQueries('session'), 15 * 60 * 1000);
    return () => {
      window.removeEventListener('focus', onFocus);
      window.clearInterval(id);
    };
  }, [queryClient]);
  return null;
}

/* Analytics page-view tracking on route change (preserved behavior). */
function RouteAnalytics() {
  const location = useLocation();
  const { t } = useTranslation();
  useEffect(() => {
    if (window.gtag) {
      window.gtag('event', 'page_view', {
        page_path: location.pathname,
        page_title: t('header.title'),
      });
    }
  }, [location.pathname, t]);
  return null;
}

function AppRoutes() {
  return (
    <Routes>
      {/* PUBLIC */}
      <Route element={<AppShell />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/marketplace" element={<MarketplacePage />} />
        <Route path="/marketplace/:listingId" element={<MineralDetailPage />} />
        <Route path="/how-it-works" element={<HowItWorksPage />} />
        <Route path="/news" element={<NewsPage />} />
        <Route path="/traceability" element={<TraceabilityPage />} />
        <Route path="/compliance" element={<CompliancePage />} />
        <Route path="/esg" element={<EsgPage />} />
        <Route path="/support" element={<SupportPage />} />
      </Route>

      {/* AUTH (own split layout, no shell) */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* USER WORKSPACE (protected) */}
      <Route element={<AppShell />}>
        <Route path="/dashboard" element={<Navigate to="/swarm" replace />} />
        <Route path="/deals" element={<FeatureGuard><DealsPage /></FeatureGuard>} />
        <Route path="/messages" element={<FeatureGuard><MessagesPage /></FeatureGuard>} />
        <Route path="/contracts" element={<FeatureGuard><ContractsPage /></FeatureGuard>} />
        <Route path="/escrow" element={<FeatureGuard><EscrowPage /></FeatureGuard>} />
        <Route path="/logistics" element={<FeatureGuard><LogisticsPage /></FeatureGuard>} />
        <Route path="/profile" element={<FeatureGuard><ProfilePage /></FeatureGuard>} />
        <Route path="/security" element={<FeatureGuard><SecurityPage /></FeatureGuard>} />
      </Route>

      {/* ADMIN (role-protected) */}
      <Route element={<AppShell />}>
        <Route path="/admin" element={<FeatureGuard requireAdmin><AdminPage /></FeatureGuard>} />
      </Route>

      {/* ---------- LEGACY ROUTES (preserved verbatim, §65/§66) ---------- */}
      <Route path="/checkout" element={<UnifiedCheckoutUI />} />
      <Route path="/swarm" element={<GlobalSwarmDashboard />} />
      <Route path="/planetary" element={<PlanetaryUI />} />
      <Route path="/localization-demo" element={<LocalizationDemo />} />
      <Route path="/mobile" element={<MobileThumbZone />} />

      {/* PRESERVED: legacy catch-all redirects unknown paths home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
