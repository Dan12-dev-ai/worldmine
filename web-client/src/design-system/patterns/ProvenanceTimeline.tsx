/**
 * World Mine — ProvenanceTimeline (§26).
 * The visual provenance spine: MINE → … → DELIVERY. Every node can reveal
 * evidence when the backend provides it; nodes never invent evidence (§38).
 */
import { useState } from "react";

export interface ProvenanceNode {
  stage: string;
  label: string;
  timestamp?: string | null;
  actor?: string | null;
  evidence?: { id: string; label: string; kind: string; url?: string }[] | null;
  note?: string | null;
}

export function ProvenanceTimeline({ nodes }: { nodes: ProvenanceNode[] }) {
  const [openIdx, setOpenIdx] = useState<number | null>(null);

  return (
    <ol style={{ listStyle: 'none', margin: 0, padding: 0 }}>
      {nodes.map((node, i) => {
        const hasEvidence = Array.isArray(node.evidence) && node.evidence.length > 0;
        const open = openIdx === i;
        return (
          <li key={`${node.stage}-${i}`} style={{ display: 'grid', gridTemplateColumns: '28px 1fr', gap: 12, position: 'relative', paddingBottom: 20 }}>
            {i < nodes.length - 1 && (
              <span aria-hidden="true" style={{ position: 'absolute', left: 13, top: 28, bottom: 2, width: 2, background: 'var(--wm-slate)' }} />
            )}
            <span
              aria-hidden="true"
              style={{
                width: 28, height: 28, borderRadius: '50%', display: 'grid', placeItems: 'center',
                background: hasEvidence ? 'var(--wm-verified-bg)' : 'var(--wm-stone)',
                border: hasEvidence ? 'var(--border-gold)' : 'var(--border-hairline)',
                color: hasEvidence ? 'var(--wm-verified)' : 'var(--wm-ash)',
                fontSize: 12, zIndex: 1,
              }}
            >
              {hasEvidence ? '✓' : i + 1}
            </span>
            <div>
              <button
                type="button"
                onClick={() => setOpenIdx(open ? null : i)}
                aria-expanded={open}
                style={{
                  background: 'none', border: 0, padding: 0, cursor: 'pointer', textAlign: 'left',
                  color: 'var(--wm-porcelain)', font: 'inherit', fontWeight: 600, display: 'block',
                }}
              >
                {node.label}
                {node.timestamp && (
                  <span style={{ fontWeight: 400, color: 'var(--wm-ash)', fontSize: 'var(--text-caption)', marginLeft: 8, fontFamily: 'var(--font-mono)' }}>
                    {new Date(node.timestamp).toLocaleDateString()}
                  </span>
                )}
              </button>
              {node.actor && (
                <div style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-ash)' }}>by {node.actor}</div>
              )}
              {open && (
                <div style={{ marginTop: 8, fontSize: 'var(--text-small)', color: 'var(--wm-fog)' }}>
                  {node.note && <p style={{ margin: '0 0 6px' }}>{node.note}</p>}
                  {hasEvidence ? (
                    <ul style={{ margin: 0, paddingLeft: 16 }}>
                      {node.evidence!.map((ev) => (
                        <li key={ev.id}>
                          {ev.url ? (
                            <a href={ev.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--wm-gold-soft)' }}>{ev.label}</a>
                          ) : (
                            <span>{ev.label} <span className="wm-badge wm-badge--neutral" style={{ marginLeft: 6 }}>{ev.kind}</span></span>
                          )}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <span style={{ color: 'var(--wm-ash)' }}>Evidence not yet available for this stage.</span>
                  )}
                </div>
              )}
            </div>
          </li>
        );
      })}
    </ol>
  );
}
