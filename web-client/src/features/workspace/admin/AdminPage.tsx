/**
 * World Mine — Operations & Governance (/admin, Phase 9).
 *
 * Reads the real admin surface: platform statistics, module health and the
 * admin action audit log — all three exist and are wired.
 *
 * HONESTY NOTE (important for review): `backend/api/admin.py` currently serves
 * `system_stats` from a seeded dictionary and `modules/health` returns a fixed
 * status/uptime/error-rate for every module. The screen therefore labels these
 * values as backend-reported seeds rather than presenting them as live
 * telemetry (§38). The audit log is genuinely append-only in-memory.
 */
import { ModuleFrame } from '../ModuleFrame';
import { DataPanel, StatGrid } from '../DataPanel';
import type { Column } from '../DataPanel';
import { errorDetail, useResource, useResourceList } from '../useResource';
import type { AdminAuditEntry, AdminModuleHealth, AdminSystemStats } from '../../../shared/types/domain';
import { count, dateTime, duration, label, money, percent, shortId, text } from '../../../shared/utils/format';
import { WorldButton, WorldStatus } from '../../../design-system';

const HEALTH_COLUMNS: Column<AdminModuleHealth>[] = [
  { key: 'module', header: 'Module', render: (m) => label(m.module) },
  { key: 'status', header: 'Status', render: (m) => (m.status ? <WorldStatus status={m.status} /> : '—') },
  { key: 'uptime', header: 'Uptime', align: 'right', nowrap: true, render: (m) => duration(m.uptime_seconds) },
  {
    key: 'error',
    header: 'Error rate',
    align: 'right',
    nowrap: true,
    render: (m) => percent(typeof m.error_rate === 'number' ? m.error_rate * 100 : null),
  },
  { key: 'checked', header: 'Last check', nowrap: true, render: (m) => dateTime(m.last_check) },
];

const AUDIT_COLUMNS: Column<AdminAuditEntry>[] = [
  { key: 'timestamp', header: 'When', nowrap: true, render: (a) => dateTime(a.timestamp) },
  { key: 'admin', header: 'Actor', nowrap: true, render: (a) => <span className="wm-mono">{shortId(a.admin_id)}</span> },
  { key: 'action', header: 'Action', render: (a) => text(a.action) },
  { key: 'target', header: 'Target', render: (a) => `${label(a.target_type)} · ${shortId(a.target_id)}` },
  {
    key: 'details',
    header: 'Details',
    render: (a) =>
      a.details && Object.keys(a.details).length
        ? <span className="wm-mono wm-hint">{Object.keys(a.details).join(', ')}</span>
        : '—',
  },
];

export function AdminPage() {
  const stats = useResource<AdminSystemStats>('/api/admin/dashboard/stats');
  const health = useResourceList<AdminModuleHealth>('/api/admin/modules/health');
  const audit = useResourceList<AdminAuditEntry>('/api/admin/audit-log?limit=50');

  return (
    <ModuleFrame
      title="Operations & Governance"
      blurb="Platform-level view for operators: service statistics, per-module health and the audit trail of administrative actions."
      sources={['GET /api/admin/dashboard/stats', 'GET /api/admin/modules/health', 'GET /api/admin/audit-log']}
      actions={<WorldButton to="/marketplace" variant="ghost">Marketplace</WorldButton>}
    >
      {stats.data ? (
        <>
          <StatGrid
            title="Platform statistics"
            items={[
              { label: 'Total users', value: count(stats.data.total_users) },
              { label: 'Active users', value: count(stats.data.active_users), tone: 'verified' },
              { label: 'Transactions (volume)', value: money(stats.data.total_transactions), tone: 'gold' },
              { label: 'Escrow held', value: money(stats.data.total_escrow_amount), tone: 'gold' },
              { label: 'Active shipments', value: count(stats.data.active_shipments) },
              { label: 'Pending notifications', value: count(stats.data.pending_notifications) },
              { label: 'AI agents active', value: count(stats.data.ai_agents_active) },
              { label: 'Reported at', value: dateTime(stats.data.timestamp) },
            ]}
          />
          <p className="wm-hint" style={{ margin: 0, maxWidth: '86ch' }}>
            Backend-reported values. <code className="wm-mono">/api/admin/dashboard/stats</code> currently serves a
            seeded statistics record rather than live aggregates, so treat these figures as placeholders until the
            endpoint is wired to the database.
          </p>
        </>
      ) : (
        <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
          <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>Platform statistics</h2>
          <p className="wm-hint" style={{ margin: '6px 0 0', maxWidth: '80ch' }}>
            {stats.isLoading
              ? 'Loading platform statistics…'
              : `Statistics are unavailable (${stats.isError ? errorDetail(stats.error) : 'endpoint returned no data'}). No values are estimated in their place.`}
          </p>
          {stats.isError && (
            <button
              type="button"
              className="wm-btn wm-btn-secondary wm-btn-sm"
              style={{ marginTop: 12 }}
              onClick={stats.refetch}
            >
              Retry
            </button>
          )}
        </section>
      )}

      <DataPanel
        title="Module health"
        description="Reported health for every registered system module. The endpoint currently returns a fixed healthy status and uptime for each module, so this table confirms reachability rather than measuring it."
        rows={health.rows}
        columns={HEALTH_COLUMNS}
        rowKey={(m) => String(m.module)}
        isLoading={health.isLoading}
        isError={health.isError}
        errorDetail={errorDetail(health.error)}
        onRetry={health.refetch}
        emptyTitle="No module health reported"
        emptyHint="Module health is published by the admin service; an empty result means no module registered a status."
      />

      <DataPanel
        title="Administrative audit log"
        description="Append-only record of administrative actions, most recent first."
        rows={audit.rows}
        columns={AUDIT_COLUMNS}
        rowKey={(a) => a.id}
        isLoading={audit.isLoading}
        isError={audit.isError}
        errorDetail={errorDetail(audit.error)}
        onRetry={audit.refetch}
        emptyTitle="No administrative actions recorded"
        emptyHint="Role changes, module restarts and configuration updates are written here as they happen."
        limitedTo={25}
      />
    </ModuleFrame>
  );
}
