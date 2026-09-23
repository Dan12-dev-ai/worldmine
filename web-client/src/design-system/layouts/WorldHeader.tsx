/**
 * World Mine — global header (Phase 2 core shell).
 * Contextual navigation: public links for visitors, workspace links for
 * authenticated users, admin tools for admins (§11, §37 role-aware routing).
 */
import { useState } from "react";
import { Link, NavLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useSession } from '../../app/providers/SessionContext';

export function WorldHeader() {
  const { t } = useTranslation();
  const { isAuthenticated, isAdmin, user } = useSession();
  const [open, setOpen] = useState(false);

  const navClass = ({ isActive }: { isActive: boolean }) =>
    `wm-navlink${isActive ? ' active' : ''}`;

  return (
    <header className="wm-header">
      <div className="wm-header__inner">
        <Link to="/" className="wm-logo" aria-label="World Mine — home">
          <img
            src="/world-mine-logo.png"
            alt=""
            className="wm-logo__img"
            width={48}
            height={48}
          />
          <span className="wm-logo__name">WORLD <span>MINE</span></span>
        </Link>

        <nav className={`wm-header__nav${open ? ' wm-header__nav--open' : ''}`} aria-label="Primary">
          <NavLink to="/marketplace" className={navClass} onClick={() => setOpen(false)}>
            {t('nav.marketplace')}
          </NavLink>
          {isAuthenticated && (
            <>
              <NavLink to="/dashboard" className={navClass} onClick={() => setOpen(false)}>
                {t('nav.dashboard')}
              </NavLink>
              <NavLink to="/deals" className={navClass} onClick={() => setOpen(false)}>
                Deals
              </NavLink>
              <NavLink to="/contracts" className={navClass} onClick={() => setOpen(false)}>
                Contracts
              </NavLink>
              <NavLink to="/escrow" className={navClass} onClick={() => setOpen(false)}>
                Escrow
              </NavLink>
              <NavLink to="/logistics" className={navClass} onClick={() => setOpen(false)}>
                Logistics
              </NavLink>
            </>
          )}
          {isAdmin && (
            <NavLink to="/admin" className={navClass} onClick={() => setOpen(false)}>
              Admin
            </NavLink>
          )}
        </nav>

        <div className="wm-header__actions">
          {isAuthenticated ? (
            <>
              <span
                className={`wm-badge ${user?.is_verified ? 'wm-badge--verified' : 'wm-badge--neutral'} wm-tip`}
                data-tip={`Verification: ${user?.is_verified ? 'verified' : (user?.kyc_status ?? 'not verified')}`}
              >
                <span className="wm-badge__dot" />
                {user?.first_name || user?.email || 'Account'}
              </span>
              <Link to="/security" className="wm-btn wm-btn-ghost wm-btn-sm">Security</Link>
            </>
          ) : (
            <>
              <Link to="/login" className="wm-btn wm-btn-ghost wm-btn-sm">{t('nav.login')}</Link>
              <Link to="/register" className="wm-btn wm-btn-primary wm-btn-sm">{t('nav.register')}</Link>
            </>
          )}
          <button
            type="button"
            className="wm-burger"
            aria-expanded={open}
            aria-label="Toggle navigation menu"
            onClick={() => setOpen((v) => !v)}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden="true">
              {open ? (
                <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              ) : (
                <path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              )}
            </svg>
          </button>
        </div>
      </div>
    </header>
  );
}
