/**
 * World Mine — global footer (Phase 2).
 */
import 'react';
import { Link } from 'react-router-dom';

export function WorldFooter() {
  return (
    <footer className="wm-footer">
      <div className="wm-footer__grid">
        <div>
          <div className="wm-logo" style={{ marginBottom: 12 }}>
            <img src="/world-mine-logo.png" alt="" className="wm-logo__img" width={44} height={44} />
            <span className="wm-logo__name">WORLD <span>MINE</span></span>
          </div>
          <p style={{ fontSize: 'var(--text-small)', maxWidth: '34ch' }}>
            Physical mineral commerce, made digitally verifiable. From mine to market — with evidence at every step.
          </p>
        </div>
        <div>
          <h4>Marketplace</h4>
          <Link to="/marketplace">Explore Minerals</Link>
          <Link to="/marketplace?view=map">Origin Map</Link>
          <Link to="/register">Become a Seller</Link>
        </div>
        <div>
          <h4>Platform</h4>
          <Link to="/traceability">Traceability</Link>
          <Link to="/compliance">Compliance</Link>
          <Link to="/esg">ESG</Link>
          <Link to="/security">Security</Link>
        </div>
        <div>
          <h4>Company</h4>
          <Link to="/how-it-works">How It Works</Link>
          <Link to="/news">Mineral News</Link>
          <Link to="/support">Support</Link>
        </div>
      </div>
      <div className="wm-footer__legal">
        <span>© {new Date().getFullYear()} World Mine. All rights reserved.</span>
        <span className="wm-mono">Institutional mineral trading infrastructure</span>
      </div>
    </footer>
  );
}
