/**
 * World Mine — Logistics (/logistics, Phase 8).
 *
 * Reads `GET /api/logistics/shipments` and supports a tracking lookup by
 * tracking number (`GET /api/logistics/track/{tracking_number}`) — the exact
 * legacy contract. Shipments live in an in-memory backend store today, so the
 * register clears on restart; the screen says so rather than implying a
 * permanent manifest. Tracking is a read-only GET and is safe to retry.
 */
import { useState } from 'react';
import { ModuleFrame } from '../ModuleFrame';
import { DataPanel } from '../DataPanel';
import type { Column } from '../DataPanel';
import { errorDetail, useResource, useResourceList } from '../useResource';
import type { Shipment, TrackingEvent } from '../../../shared/types/domain';
import { address, dateTime, label, shortId, text, weight } from '../../../shared/utils/format';
import { WorldBadge, WorldButton, WorldStatus } from '../../../design-system';

const COLUMNS: Column<Shipment>[] = [
  {
    key: 'tracking',
    header: 'Tracking',
    nowrap: true,
    render: (s) => <span className="wm-mono">{shortId(s.tracking_number, 12)}</span>,
  },
  { key: 'status', header: 'Status', render: (s) => (s.status ? <WorldStatus status={s.status} /> : '—') },
  { key: 'mode', header: 'Mode', render: (s) => label(s.transport_mode) },
  { key: 'origin', header: 'Origin', render: (s) => address(s.origin_address) },
  { key: 'destination', header: 'Destination', render: (s) => address(s.destination_address) },
  { key: 'weight', header: 'Weight', align: 'right', nowrap: true, render: (s) => weight(s) },
  { key: 'eta', header: 'Estimated', nowrap: true, render: (s) => dateTime(s.estimated_delivery) },
  { key: 'delivered', header: 'Delivered', nowrap: true, render: (s) => dateTime(s.actual_delivery) },
];

export function LogisticsPage() {
  const shipments = useResourceList<Shipment>('/api/logistics/shipments?limit=50');
  const [trackingNumber, setTrackingNumber] = useState('');
  const [lookup, setLookup] = useState<string | null>(null);

  return (
    <ModuleFrame
      title="Logistics"
      blurb="Shipment register with transport mode, route, weight and delivery state, plus tracking lookup by tracking number."
      sources={['GET /api/logistics/shipments', 'GET /api/logistics/track/{tracking_number}', 'GET /api/logistics/shipments/{id}/tracking']}
      actions={<WorldButton to="/escrow" variant="ghost">Escrow</WorldButton>}
    >
      <form
        className="wm-surface"
        style={{ padding: 'var(--space-5)', display: 'flex', gap: 'var(--space-4)', alignItems: 'flex-end', flexWrap: 'wrap' }}
        onSubmit={(ev) => {
          ev.preventDefault();
          const value = trackingNumber.trim();
          setLookup(value ? value : null);
        }}
      >
        <label className="wm-field" style={{ flex: '1 1 280px' }}>
          <span className="wm-label">Track a shipment</span>
          <input
            className="wm-input"
            value={trackingNumber}
            onChange={(ev) => setTrackingNumber(ev.target.value)}
            placeholder="Enter a tracking number"
            autoComplete="off"
          />
        </label>
        <button type="submit" className="wm-btn wm-btn-primary wm-btn-sm" disabled={!trackingNumber.trim()}>
          Track
        </button>
        {lookup && (
          <button
            type="button"
            className="wm-btn wm-btn-ghost wm-btn-sm"
            onClick={() => {
              setLookup(null);
              setTrackingNumber('');
            }}
          >
            Clear
          </button>
        )}
      </form>

      {lookup && <TrackingLookup trackingNumber={lookup} />}

      <DataPanel
        title="Shipment register"
        description="Served from the in-memory logistics store today — entries are cleared when the backend restarts."
        rows={shipments.rows}
        columns={COLUMNS}
        rowKey={(s, i) => s.id ?? s.tracking_number ?? `shipment-${i}`}
        isLoading={shipments.isLoading}
        isError={shipments.isError}
        errorDetail={errorDetail(shipments.error)}
        onRetry={shipments.refetch}
        emptyTitle="No shipments on record"
        emptyHint="A shipment is created once a funded deal enters the shipping stage; its tracking number is issued at that point."
        limitedTo={25}
      />
    </ModuleFrame>
  );
}

function TrackingLookup({ trackingNumber }: { trackingNumber: string }) {
  const shipment = useResource<Shipment>(`/api/logistics/track/${encodeURIComponent(trackingNumber)}`);
  const events = useResource<TrackingEvent[]>(
    `/api/logistics/shipments/${encodeURIComponent(shipment.data?.id ?? '')}/tracking`,
    { enabled: !!shipment.data?.id },
  );

  return (
    <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap', alignItems: 'baseline' }}>
        <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>
          Tracking <span className="wm-mono">{trackingNumber}</span>
        </h2>
        <button type="button" className="wm-btn wm-btn-secondary wm-btn-sm" onClick={shipment.refetch}>
          Refresh
        </button>
      </div>

      {shipment.isLoading && <p className="wm-hint" style={{ marginTop: 10 }}>Looking up shipment…</p>}

      {shipment.isError && (
        <p className="wm-hint" style={{ marginTop: 10, color: '#E88B84' }}>
          No shipment found for this tracking number ({errorDetail(shipment.error)}).
        </p>
      )}

      {shipment.data && (
        <>
          <dl style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))', gap: 'var(--space-4)', margin: 'var(--space-5) 0 0' }}>
            <div>
              <dt className="wm-label">Status</dt>
              <dd style={{ margin: 0 }}>{shipment.data.status ? <WorldStatus status={shipment.data.status} /> : '—'}</dd>
            </div>
            <div>
              <dt className="wm-label">Mode</dt>
              <dd style={{ margin: 0 }}>{label(shipment.data.transport_mode)}</dd>
            </div>
            <div>
              <dt className="wm-label">Order</dt>
              <dd className="wm-mono" style={{ margin: 0 }}>{shortId(shipment.data.order_id)}</dd>
            </div>
            <div>
              <dt className="wm-label">Weight</dt>
              <dd className="wm-mono" style={{ margin: 0 }}>{weight(shipment.data)}</dd>
            </div>
            <div>
              <dt className="wm-label">Estimated delivery</dt>
              <dd className="wm-mono" style={{ margin: 0 }}>{dateTime(shipment.data.estimated_delivery)}</dd>
            </div>
            <div>
              <dt className="wm-label">Actual delivery</dt>
              <dd className="wm-mono" style={{ margin: 0 }}>{dateTime(shipment.data.actual_delivery)}</dd>
            </div>
          </dl>

          <h3 style={{ margin: 'var(--space-5) 0 8px', fontSize: 'var(--text-body)' }}>Movement history</h3>
          {events.isLoading && <p className="wm-hint" style={{ margin: 0 }}>Loading events…</p>}
          {events.isError && (
            <p className="wm-hint" style={{ margin: 0 }}>
              Movement history is unavailable ({errorDetail(events.error)}). The shipment record above is unaffected.
            </p>
          )}
          {events.data && events.data.length === 0 && (
            <p className="wm-hint" style={{ margin: 0 }}>No movement events have been recorded for this shipment yet.</p>
          )}
          {events.data && events.data.length > 0 && (
            <ol style={{ margin: 0, paddingLeft: '1.1em', display: 'grid', gap: 10 }}>
              {events.data.map((ev) => (
                <li key={ev.id}>
                  <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
                    {ev.status ? <WorldStatus status={ev.status} /> : <WorldBadge tone="neutral">event</WorldBadge>}
                    <span className="wm-hint">{dateTime(ev.timestamp)}</span>
                  </div>
                  <div>{text(ev.description)}</div>
                  {ev.location && (
                    <div className="wm-mono wm-hint">
                      {ev.location.latitude}, {ev.location.longitude}
                    </div>
                  )}
                </li>
              ))}
            </ol>
          )}
        </>
      )}
    </section>
  );
}
