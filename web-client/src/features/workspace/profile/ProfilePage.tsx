/**
 * World Mine — Profile Studio (/profile, Phase 8).
 *
 * Identity comes from the live session (`GET /api/auth/me`, which the session
 * provider already owns — no duplicate request) and identity documents from
 * `GET /api/kyc/documents`. Verification state is displayed exactly as the
 * server reports it; the UI never upgrades "pending" to "verified" (§38).
 */
import { ModuleFrame } from '../ModuleFrame';
import { DataPanel } from '../DataPanel';
import type { Column } from '../DataPanel';
import { useSession } from '../../../app/providers/SessionContext';
import { errorDetail, useResourceList } from '../useResource';
import type { KycDocument } from '../../../shared/types/domain';
import { dateTime, label, shortId, text } from '../../../shared/utils/format';
import { WorldBadge, WorldButton, WorldEmptyState } from '../../../design-system';

const DOCUMENT_COLUMNS: Column<KycDocument>[] = [
  {
    key: 'type',
    header: 'Document',
    render: (d) => label(d.document_type ?? null),
  },
  { key: 'status', header: 'Status', render: (d) => <WorldBadge tone={d.status === 'verified' ? 'verified' : 'pending'}>{label(d.status ?? null)}</WorldBadge> },
  {
    key: 'verification',
    header: 'Verification',
    nowrap: true,
    render: (d) => <span className="wm-mono">{shortId(d.verification_id ?? d.id ?? null)}</span>,
  },
  { key: 'uploaded', header: 'Uploaded', nowrap: true, render: (d) => dateTime(d.uploaded_at) },
  { key: 'reviewed', header: 'Reviewed', nowrap: true, render: (d) => dateTime(d.reviewed_at ?? null) },
];

export function ProfilePage() {
  const { user, isLoading } = useSession();
  const documents = useResourceList<KycDocument>('/api/kyc/documents', { enabled: !!user });

  if (isLoading) {
    return (
      <ModuleFrame title="Profile Studio" blurb="Loading your identity and verification state…" sources={['GET /api/auth/me']}>
        <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
          <div className="wm-skeleton" style={{ height: 160 }} />
        </section>
      </ModuleFrame>
    );
  }

  if (!user) {
    return (
      <ModuleFrame
        title="Profile Studio"
        blurb="Your identity, verification level and identity documents."
        sources={['GET /api/auth/me', 'GET /api/kyc/documents']}
      >
        <div className="wm-surface" style={{ padding: 'var(--space-6)' }}>
          <WorldEmptyState
            title="Sign in to view your profile"
            hint="Profile data is served for the authenticated identity only."
            action={<WorldButton to="/login" variant="primary" size="sm">Sign in</WorldButton>}
          />
        </div>
      </ModuleFrame>
    );
  }

  const fullName = [user.first_name, user.last_name].filter(Boolean).join(' ');

  return (
    <ModuleFrame
      title="Profile Studio"
      blurb="Your identity, verification level and identity documents."
      sources={['GET /api/auth/me', 'GET /api/kyc/documents']}
      actions={<WorldButton to="/security" variant="secondary">Security</WorldButton>}
    >
      <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>{fullName || text(user.email)}</h2>
          <WorldBadge tone={user.is_verified ? 'verified' : 'pending'}>
            {user.is_verified ? 'identity verified' : 'verification incomplete'}
          </WorldBadge>
        </div>

        <dl
          style={{
            display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 'var(--space-4)', margin: 'var(--space-5) 0 0',
          }}
        >
          <div>
            <dt className="wm-label">Email</dt>
            <dd style={{ margin: 0 }}>{text(user.email)}</dd>
          </div>
          <div>
            <dt className="wm-label">Account reference</dt>
            <dd className="wm-mono" style={{ margin: 0 }}>{shortId(user.id, 12)}</dd>
          </div>
          <div>
            <dt className="wm-label">KYC status</dt>
            <dd style={{ margin: 0 }}>{label(user.kyc_status)}</dd>
          </div>
          <div>
            <dt className="wm-label">KYC level</dt>
            <dd style={{ margin: 0 }}>{label(user.kyc_level)}</dd>
          </div>
          <div>
            <dt className="wm-label">Member since</dt>
            <dd className="wm-mono" style={{ margin: 0 }}>{dateTime(user.created_at)}</dd>
          </div>
          <div>
            <dt className="wm-label">Last sign-in</dt>
            <dd className="wm-mono" style={{ margin: 0 }}>{dateTime(user.last_login)}</dd>
          </div>
        </dl>

        <p className="wm-hint" style={{ marginTop: 'var(--space-5)', maxWidth: '72ch' }}>
          Trading statistics (reputation, ESG score, volume) belong to the marketplace user model and are
          not exposed by <code className="wm-mono">/api/auth/me</code> today — so they are not estimated here.
          Role-based navigation also stays disabled until the endpoint returns a role claim.
        </p>
      </section>

      <DataPanel
        title="Identity documents"
        description="Documents submitted for verification, with their review state."
        rows={documents.rows}
        columns={DOCUMENT_COLUMNS}
        rowKey={(d, i) => d.id ?? d.verification_id ?? `document-${i}`}
        isLoading={documents.isLoading}
        isError={documents.isError}
        errorDetail={errorDetail(documents.error)}
        onRetry={documents.refetch}
        emptyTitle="No identity documents"
        emptyHint="Uploaded verification documents appear here once the KYC submission flow is available."
        limitedTo={20}
      />
    </ModuleFrame>
  );
}
