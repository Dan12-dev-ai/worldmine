/**
 * World Mine — auth split layout (§13).
 * LEFT: brand + geological environment. RIGHT: secure auth workspace.
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { LifecycleStepper } from '../../design-system/patterns/LifecycleStepper';

export function AuthSplitLayout({
  brandTitle, brandBody, children,
}: { brandTitle: string; brandBody: string; children: React.ReactNode }) {
  return (
    <div className="wm-auth">
      <aside className="wm-auth__brand" aria-hidden="true">
        <div>
          <Link to="/" className="wm-logo">
            <img src="/world-mine-logo.png" alt="" className="wm-logo__img" width={44} height={44} />
            <span className="wm-logo__name">WORLD <span>MINE</span></span>
          </Link>
        </div>
        <div>
          <h2 style={{ fontSize: 'var(--text-h2)', maxWidth: '22ch' }}>{brandTitle}</h2>
          <p style={{ color: 'var(--wm-fog)', maxWidth: '38ch' }}>{brandBody}</p>
        </div>
        <div style={{ opacity: 0.85 }}>
          <LifecycleStepper />
        </div>
      </aside>
      <section className="wm-auth__panel">
        {children}
      </section>
    </div>
  );
}
