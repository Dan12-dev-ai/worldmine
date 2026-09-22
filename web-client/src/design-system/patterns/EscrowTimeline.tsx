/**
 * World Mine — EscrowTimeline (§24).
 * Extremely clear state machine. Each state explains: current state, next state,
 * responsible party, required action. Financial actions require explicit
 * confirmation by the caller — this component only visualizes.
 */
import 'react';
import type { EscrowStatus } from '../../shared/types/domain';

const FLOW: { key: EscrowStatus; label: string; actor: string; action: string }[] = [
  { key: 'created',    label: 'Created',        actor: 'System',            action: 'Deal terms recorded' },
  { key: 'funded',     label: 'Buyer payment',  actor: 'Buyer',             action: 'Fund the escrow' },
  { key: 'locked',     label: 'Escrow funded',  actor: 'Escrow',            action: 'Funds held — cannot be moved unilaterally' },
  { key: 'pending_verification', label: 'Inspection & shipment', actor: 'Seller / Inspector', action: 'Deliver + pass inspection' },
  { key: 'released',   label: 'Seller payment', actor: 'Escrow',            action: 'Release conditions met' },
];

const TERMINAL: Record<string, { tone: string; note: string }> = {
  disputed:  { tone: 'wm-badge--error',   note: 'Dispute opened — funds frozen pending resolution' },
  resolved:  { tone: 'wm-badge--neutral', note: 'Dispute resolved by agreed terms' },
  cancelled: { tone: 'wm-badge--neutral', note: 'Escrow cancelled — no funds moved' },
  refunded:  { tone: 'wm-badge--error',   note: 'Funds returned to buyer' },
};

export function EscrowTimeline({ status }: { status: EscrowStatus }) {
  const terminal = TERMINAL[status];

  if (terminal) {
    return (
      <div className="wm-state" style={{ padding: 'var(--space-6) var(--space-5)' }}>
        <span className={`wm-badge ${terminal.tone}`} style={{ fontSize: 'var(--text-small)' }}>
          <span className="wm-badge__dot" />{status.toUpperCase()}
        </span>
        <p style={{ margin: 0, maxWidth: '46ch' }}>{terminal.note}</p>
      </div>
    );
  }

  const activeIdx = FLOW.findIndex((s) => s.key === status);
  const next = activeIdx >= 0 && activeIdx < FLOW.length - 1 ? FLOW[activeIdx + 1] : null;

  return (
    <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'flex', flexDirection: 'column', gap: 0 }}>
      {FLOW.map((stage, i) => {
        const done = activeIdx > i;
        const active = activeIdx === i;
        return (
          <li
            key={stage.key}
            style={{
              display: 'grid', gridTemplateColumns: '24px 1fr', gap: 12,
              position: 'relative', paddingBottom: 24,
            }}
          >
            {/* connector */}
            {i < FLOW.length - 1 && (
              <span
                aria-hidden="true"
                style={{
                  position: 'absolute', left: 11, top: 24, bottom: 4, width: 2,
                  background: done ? 'var(--wm-verified-line)' : 'var(--wm-slate)',
                }}
              />
            )}
            <span
              aria-hidden="true"
              style={{
                width: 24, height: 24, borderRadius: '50%', display: 'grid', placeItems: 'center',
                fontSize: 11, fontWeight: 700, zIndex: 1,
                background: done ? 'var(--wm-verified)' : active ? 'var(--wm-gold)' : 'var(--wm-stone)',
                color: done || active ? '#14110A' : 'var(--wm-ash)',
                border: active ? '2px solid var(--wm-gold-soft)' : '1px solid var(--wm-slate)',
              }}
            >
              {done ? '✓' : i + 1}
            </span>
            <div>
              <div style={{ fontWeight: 600, color: active ? 'var(--wm-gold-soft)' : done ? 'var(--wm-porcelain)' : 'var(--wm-ash)' }}>
                {stage.label} {active && <span className="wm-badge wm-badge--gold">CURRENT</span>}
              </div>
              <div style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-ash)' }}>
                Responsible: {stage.actor} — {stage.action}
              </div>
              {active && next && (
                <div style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-fog)', marginTop: 4 }}>
                  Next: {next.label} ({next.actor})
                </div>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
