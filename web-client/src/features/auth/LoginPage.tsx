/**
 * World Mine — Login (Phase 4, §13/§14).
 * Split-brand layout. Uses the password /api/auth/login contract.
 * Never invents a magic-link flow the login endpoint doesn't provide —
 * the register page handles magic-link copy faithfully.
 */
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useSession } from '../../app/providers/SessionContext';
import { WorldButton } from '../../design-system';
import { AuthSplitLayout } from './AuthSplitLayout';

export function LoginPage() {
  const { refetch } = useSession();
  const navigate = useNavigate();
  const location = useLocation();
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const from = (location.state as { from?: string } | null)?.from ?? '/dashboard';

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username_or_email: identifier, password }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail?.message ?? body?.detail ?? 'Sign-in failed. Check your credentials and try again.');
      }
      refetch();
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Sign-in failed. Please try again.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthSplitLayout
      brandTitle="Access your trading workspace"
      brandBody="Deals, contracts, escrow and logistics — one secure room for every transaction."
    >
      <h1 style={{ fontSize: 'var(--text-h1)' }}>Sign in</h1>
      <form onSubmit={handleSubmit} className="wm-auth__card" noValidate>
        {error && (
          <div role="alert" className="wm-badge wm-badge--error" style={{ padding: 10, borderRadius: 'var(--radius-md)', textTransform: 'none', fontSize: 'var(--text-small)' }}>
            <span className="wm-badge__dot" />{error}
          </div>
        )}
        <div className="wm-field">
          <label className="wm-label" htmlFor="login-id">Email or username</label>
          <input
            id="login-id" className="wm-input" autoComplete="username"
            value={identifier} onChange={(e) => setIdentifier(e.target.value)}
            required autoFocus
          />
        </div>
        <div className="wm-field">
          <label className="wm-label" htmlFor="login-pw">Password</label>
          <input
            id="login-pw" className="wm-input" type="password" autoComplete="current-password"
            value={password} onChange={(e) => setPassword(e.target.value)}
            required minLength={8}
          />
        </div>
        <WorldButton type="submit" block disabled={busy || !identifier || !password} aria-busy={busy}>
          {busy ? 'Signing in…' : 'Sign in'}
        </WorldButton>
        <p style={{ margin: 0, fontSize: 'var(--text-small)', color: 'var(--wm-ash)', textAlign: 'center' }}>
          No account yet? <Link to="/register" style={{ color: 'var(--wm-gold-soft)' }}>Create one</Link>
        </p>
      </form>
    </AuthSplitLayout>
  );
}
