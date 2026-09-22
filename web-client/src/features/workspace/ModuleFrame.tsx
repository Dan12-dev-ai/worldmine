/**
 * World Mine — workspace module frame (Phase 6–9).
 *
 * Shared header for every workspace module: kicker, title, blurb, the exact API
 * endpoints the module reads, and a slot for module-level actions. Keeps the
 * eight modules visually identical without duplicating markup, and makes the
 * data provenance of each screen visible to the reviewer (anti-fabrication §38).
 */
import type { ReactNode } from 'react';

export function ModuleFrame({
  title, blurb, sources, actions, children,
}: {
  title: string;
  blurb: string;
  /** Endpoint paths the module reads, shown verbatim so they stay verifiable. */
  sources?: string[];
  actions?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="wm-container" style={{ padding: 'var(--space-8) var(--gutter)' }}>
      <div
        style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
          gap: 'var(--space-5)', flexWrap: 'wrap',
        }}
      >
        <div className="wm-section__head" style={{ margin: 0 }}>
          <span className="wm-kicker">Workspace</span>
          <h1 style={{ fontSize: 'var(--text-h1)', margin: '10px 0 8px' }}>{title}</h1>
          <p style={{ color: 'var(--wm-fog)', margin: 0, maxWidth: '68ch' }}>{blurb}</p>
        </div>
        {actions && <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>{actions}</div>}
      </div>

      {sources && sources.length > 0 && (
        <p className="wm-hint" style={{ marginTop: 14, display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
          <span>Data source{sources.length > 1 ? 's' : ''}:</span>
          {sources.map((s) => (
            <code key={s} className="wm-mono" style={{ color: 'var(--wm-ash)' }}>{s}</code>
          ))}
        </p>
      )}

      <div style={{ marginTop: 'var(--space-6)', display: 'grid', gap: 'var(--space-6)' }}>{children}</div>
    </div>
  );
}
