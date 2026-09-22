/**
 * World Mine — FeatureGuard (§41 route protection).
 * Route protection is UX, not authorization: the backend remains authoritative.
 * Unauthenticated users are redirected to /login with a return path.
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useSession } from '../providers/SessionContext';

export function FeatureGuard({ children, requireAdmin = false }: { children: React.ReactNode; requireAdmin?: boolean }) {
  const { isAuthenticated, isAdmin, isLoading } = useSession();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="wm-container" style={{ padding: 'var(--space-9) 0' }} role="status" aria-live="polite">
        <div className="wm-skeleton" style={{ height: 200 }} />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }
  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }
  return <>{children}</>;
}
