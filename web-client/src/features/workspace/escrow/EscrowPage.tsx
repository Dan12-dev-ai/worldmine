/**
 * World Mine — Escrow (/escrow, Phase 7).
 *
 * Contract notes (verified against backend/api/escrow.py):
 *   - the list endpoint returns an ENVELOPE `{"data": [...]}`, not a bare array
 *     — `useResourceList` normalises both shapes and reports anything else as a
 *     contract break rather than as "empty".
 *   - `?status=` IS filtered server-side (unlike marketplace).
 *   - the backend holds escrows in memory today, so the register resets when the
 *     service restarts; the screen states this instead of implying permanence.
 * Releasing, disputing or refunding funds are irreversible mutations and are
 * deliberately NOT wired to buttons here (§63: no implicit financial actions).
 */
import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ModuleFrame } from '../ModuleFrame';
import { DataPanel } from '../DataPanel';
import type { Column } from '../DataPanel';
import { errorDetail, useResourceList } from '../useResource';
import type { Escrow, EscrowStatus } from '../../../shared/types/domain';
import { ABSENT, count, dateTime, label, money, shortId, text } from '../../../shared/utils/format';
import { EscrowTimeline, WorldButton, WorldStatus } from '../../../design-system';

const STATUS_FILTERS = [
  '', 'created', 'funded', 'locked', 'pending_verification',
  'disputed', 'resolved', 'released', 'cancelled', 'refunded',
];

const BASE_COLUMNS: Column<Escrow>[] = [
  { key: 'id', header: 'Escrow', nowrap: true, render: (e) => <span className="wm-mono">{shortId(e.id)}</span> },
  { key: 'buyer', header: 'Buyer', nowrap: true, render: (e) => <span className="wm-mono">{shortId(e.buyer_id)}</span> },
  { key: 'seller', header: 'Seller', nowrap: true, render: (e) => <span className="wm-mono">{shortId(e.seller_id)}</span> },
  { key: 'amount', header: 'Amount', align: 'right', render: (e) => money(e.amount, e.currency) },
  { key: 'status', header: 'Status', render: (e) => (e.status ? <WorldStatus status={e.status} /> : ABSENT) },
  { key: 'milestones', header: 'Milestones', align: 'right', render: (e) => count(e.milestones?.length ?? 0) },
  { key: 'auto', header: 'Auto-release', nowrap: true, render: (e) => dateTime(e.auto_release_date) },
  { key: 'updated', header: 'Updated', nowrap: true, render: (e) => dateTime(e.updated_at) },
];

export function EscrowPage() {
  const [params, setParams] = useSearchParams();
  const status = params.get('status') ?? '';
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const path = `/api/escrow/escrow?limit=50${status ? `&status=${encodeURIComponent(status)}` : ''}`;
  const escrows = useResourceList<Escrow>(path);
  const selected = escrows.rows?.find((e) => e.id === selectedId) ?? null;

  const columns: Column<Escrow>[] = [
    ...BASE_COLUMNS,
    {
      key: 'open',
      header: '',
      align: 'right',
      render: (e) => (
        <button
          type="button"
          className="wm-btn wm-btn-ghost wm-btn-sm"
          aria-pressed={e.id === selectedId}
          onClick={() => setSelectedId(e.id === selectedId ? null : e.id)}
        >
          {e.id === selectedId ? 'Close' : 'Inspect'}
        </button>
      ),
    },
  ];

  return (
    <ModuleFrame
      title="Escrow"
      blurb="Funded protection for every transaction. Each escrow shows its current state, the party responsible for the next step, and the conditions that must be met before funds move."
      sources={['GET /api/escrow/escrow', 'GET /api/escrow/escrow/{id}/status']}
      actions={<WorldButton to="/contracts" variant="secondary">Contracts</WorldButton>}
    >
      <DataPanel
        title="Escrow register"
        description="Filtering by status is applied server-side. The register is served from an in-memory store today, so entries do not survive a backend restart."
        rows={escrows.rows}
        columns={columns}
        rowKey={(e) => e.id}
        isLoading={escrows.isLoading}
        isError={escrows.isError}
        errorDetail={errorDetail(escrows.error)}
        onRetry={escrows.refetch}
        emptyTitle={status ? `No escrows with status “${status}”` : 'No escrows yet'}
        emptyHint="An escrow is created when a deal reaches the funding stage."
        limitedTo={25}
        actions={
          <label className="wm-field" style={{ minWidth: 200 }}>
            <span className="wm-label">Status filter</span>
            <select
              className="wm-input"
              value={status}
              onChange={(ev) => {
                const next = new URLSearchParams(params);
                if (ev.target.value) next.set('status', ev.target.value);
                else next.delete('status');
                setParams(next, { replace: true });
              }}
            >
              {STATUS_FILTERS.map((s) => (
                <option key={s || 'all'} value={s}>{s ? label(s) : 'All statuses'}</option>
              ))}
            </select>
          </label>
        }
      >
        {selected && (
          <div style={{ marginTop: 'var(--space-5)', borderTop: 'var(--border-hairline)', paddingTop: 'var(--space-5)' }}>
            <h3 style={{ margin: '0 0 var(--space-4)', fontSize: 'var(--text-h3)' }}>
              Escrow {shortId(selected.id, 12)}
            </h3>
            <EscrowTimeline status={selected.status as EscrowStatus} />

            <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 'var(--space-4)', margin: 'var(--space-5) 0 0' }}>
              <div>
                <dt className="wm-label">Amount</dt>
                <dd className="wm-mono" style={{ margin: 0 }}>{money(selected.amount, selected.currency)}</dd>
              </div>
              <div>
                <dt className="wm-label">Auto-release window</dt>
                <dd className="wm-mono" style={{ margin: 0 }}>
                  {typeof selected.auto_release_days === 'number' ? `${selected.auto_release_days} day(s)` : ABSENT}
                </dd>
              </div>
              <div>
                <dt className="wm-label">Payment transaction</dt>
                <dd className="wm-mono" style={{ margin: 0 }}>{shortId(selected.payment_transaction_id)}</dd>
              </div>
              <div>
                <dt className="wm-label">Transaction</dt>
                <dd className="wm-mono" style={{ margin: 0 }}>{shortId(selected.transaction_id)}</dd>
              </div>
            </dl>

            <h4 style={{ margin: 'var(--space-5) 0 8px', fontSize: 'var(--text-body)' }}>Milestones recorded</h4>
            {selected.milestones?.length ? (
              <ul style={{ margin: 0, paddingLeft: '1.1em', display: 'grid', gap: 6 }}>
                {selected.milestones.map((m) => <li key={m}>{label(m)}</li>)}
              </ul>
            ) : (
              <p className="wm-hint" style={{ margin: 0 }}>No milestone has been recorded yet.</p>
            )}

            <h4 style={{ margin: 'var(--space-5) 0 8px', fontSize: 'var(--text-body)' }}>Release conditions</h4>
            {selected.release_conditions && Object.keys(selected.release_conditions).length ? (
              <ul className="wm-mono" style={{ margin: 0, paddingLeft: '1.1em', display: 'grid', gap: 6 }}>
                {Object.entries(selected.release_conditions).map(([k, v]) => (
                  <li key={k}>{label(k)}: {text(String(v))}</li>
                ))}
              </ul>
            ) : (
              <p className="wm-hint" style={{ margin: 0 }}>
                No release conditions are stored on this escrow — funds therefore cannot be moved automatically.
              </p>
            )}

            {selected.dispute_details && (
              <>
                <h4 style={{ margin: 'var(--space-5) 0 8px', fontSize: 'var(--text-body)' }}>Dispute</h4>
                <p className="wm-hint" style={{ margin: 0 }}>
                  A dispute record exists; funds remain frozen until it is resolved.
                </p>
              </>
            )}
          </div>
        )}
      </DataPanel>
    </ModuleFrame>
  );
}
