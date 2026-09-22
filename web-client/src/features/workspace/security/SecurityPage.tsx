/**
 * World Mine — Security Center (/security, Phase 8).
 *
 * This module is deliberately a *capability report*, not a mock dashboard.
 * The auth contract today (backend/api/auth.py) exposes: register (magic-link),
 * login (password), login/magic-link, verify, refresh, logout, check-password-
 * strength, me. There is NO session list, NO session revoke, NO MFA/TOTP
 * enrolment and NO recovery-code endpoint — so those controls are listed as
 * unavailable-with-the-exact-missing-capability rather than rendered as
 * decorative buttons that would do nothing (§38/§47).
 */
import { ModuleFrame } from '../ModuleFrame';
import { useSession } from '../../../app/providers/SessionContext';
import { dateTime, label, text } from '../../../shared/utils/format';
import { WorldBadge, WorldButton } from '../../../design-system';

interface Capability {
  label: string;
  detail: string;
  available: boolean;
}

const CAPABILITIES: Capability[] = [
  {
    label: 'HttpOnly cookie sessions',
    detail: 'The typed API client sends credentials with every request (credentials: "include"), so a server-managed session cookie is used where the backend supports it.',
    available: true,
  },
  {
    label: 'Magic-link email verification',
    detail: 'POST /api/auth/register issues a one-time verification link and GET /api/auth/verify consumes it. No password is transmitted at sign-up.',
    available: true,
  },
  {
    label: 'Token refresh',
    detail: 'POST /api/auth/refresh renews the session; the client refreshes the session query on window focus and every 15 minutes.',
    available: true,
  },
  {
    label: 'Password strength checking',
    detail: 'POST /api/auth/check-password-strength is available for sign-in flows.',
    available: true,
  },
  {
    label: 'Two-factor authentication (TOTP / WebAuthn)',
    detail: 'No MFA enrolment or challenge endpoint exists in the auth contract yet, so no toggle is offered. A backend endpoint must exist before a switch can be shown honestly.',
    available: false,
  },
  {
    label: 'Active session list & remote revoke',
    detail: 'Requires a session-inventory endpoint (none exists). Without it the UI cannot show devices or force a sign-out elsewhere.',
    available: false,
  },
  {
    label: 'Recovery codes',
    detail: 'Depends on MFA enrolment; not present in the contract.',
    available: false,
  },
  {
    label: 'Suspicious-activity alerts',
    detail: 'Delivered through the notifications service when the backend emits them; the Security Center does not detect them itself.',
    available: false,
  },
];

export function SecurityPage() {
  const { user } = useSession();

  return (
    <ModuleFrame
      title="Security Center"
      blurb="What protects your account today, and exactly which controls still need a backend capability before they can be shown."
      sources={['GET /api/auth/me', 'POST /api/auth/refresh', 'POST /api/auth/logout']}
      actions={<WorldButton to="/profile" variant="secondary">Profile</WorldButton>}
    >
      <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
        <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>Current session</h2>
        {user ? (
          <dl
            style={{
              display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: 'var(--space-4)', margin: 'var(--space-4) 0 0',
            }}
          >
            <div>
              <dt className="wm-label">Identity</dt>
              <dd style={{ margin: 0 }}>{text(user.email)}</dd>
            </div>
            <div>
              <dt className="wm-label">Verification</dt>
              <dd style={{ margin: 0 }}>
                <WorldBadge tone={user.is_verified ? 'verified' : 'pending'}>
                  {user.is_verified ? 'verified' : label(user.kyc_status)}
                </WorldBadge>
              </dd>
            </div>
            <div>
              <dt className="wm-label">Last sign-in</dt>
              <dd className="wm-mono" style={{ margin: 0 }}>{dateTime(user.last_login)}</dd>
            </div>
          </dl>
        ) : (
          <p className="wm-hint" style={{ margin: '8px 0 0' }}>
            No active session. Sign in to see your session details.
          </p>
        )}
        <p className="wm-hint" style={{ marginTop: 'var(--space-4)', maxWidth: '72ch' }}>
          Device, IP and location of the current session are not returned by the auth endpoints, so they are
          deliberately not displayed. They will appear once a session-inventory endpoint exists.
        </p>
      </section>

      <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
        <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>Protections in force</h2>
        <ul style={{ margin: 'var(--space-4) 0 0', padding: 0, listStyle: 'none', display: 'grid', gap: 'var(--space-4)' }}>
          {CAPABILITIES.filter((c) => c.available).map((c) => (
            <li key={c.label} style={{ display: 'grid', gap: 4 }}>
              <span style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                <WorldBadge tone="verified"><span className="wm-badge__dot" />active</WorldBadge>
                <strong>{c.label}</strong>
              </span>
              <span className="wm-hint" style={{ maxWidth: '80ch' }}>{c.detail}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
        <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>Not yet available</h2>
        <p className="wm-hint" style={{ margin: '6px 0 var(--space-4)', maxWidth: '80ch' }}>
          These controls are intentionally absent rather than present-but-inert. Each one names the backend
          capability it depends on.
        </p>
        <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'grid', gap: 'var(--space-4)' }}>
          {CAPABILITIES.filter((c) => !c.available).map((c) => (
            <li key={c.label} style={{ display: 'grid', gap: 4 }}>
              <span style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                <WorldBadge tone="pending"><span className="wm-badge__dot" />pending backend</WorldBadge>
                <strong>{c.label}</strong>
              </span>
              <span className="wm-hint" style={{ maxWidth: '80ch' }}>{c.detail}</span>
            </li>
          ))}
        </ul>
      </section>
    </ModuleFrame>
  );
}
