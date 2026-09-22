/**
 * World Mine — app shell layout (Phase 2).
 * Wraps all standard pages: header, outlet, footer, mobile bottom nav.
 */
import 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { WorldHeader } from './WorldHeader';
import { WorldFooter } from './WorldFooter';

export function AppShell() {
  const navClass = ({ isActive }: { isActive: boolean }) =>
    `wm-navlink${isActive ? ' active' : ''}`;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <WorldHeader />
      <main id="main" style={{ flex: 1 }}>
        <Outlet />
      </main>
      <WorldFooter />
      <nav className="wm-bottomnav" aria-label="Mobile navigation">
        <NavLink to="/" className={navClass} end>Home</NavLink>
        <NavLink to="/marketplace" className={navClass}>Market</NavLink>
        <NavLink to="/dashboard" className={navClass}>Deals</NavLink>
        <NavLink to="/messages" className={navClass}>Messages</NavLink>
        <NavLink to="/profile" className={navClass}>Account</NavLink>
      </nav>
    </div>
  );
}
