/**
 * World Mine — shared UI primitives (typed, token-driven).
 * WorldButton, WorldBadge, WorldStatus, WorldSkeleton, WorldEmptyState, WorldErrorState.
 */
import React from 'react';
import { Link } from 'react-router-dom';

/* ---------- Button ---------- */
export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface WorldButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  block?: boolean;
  to?: string; // when set, renders a Link
}

const variantClass: Record<ButtonVariant, string> = {
  primary: 'wm-btn-primary',
  secondary: 'wm-btn-secondary',
  ghost: 'wm-btn-ghost',
  danger: 'wm-btn-danger',
};

export function WorldButton({
  variant = 'primary', size = 'md', block, to, className = '', children, ...rest
}: WorldButtonProps) {
  const cls = [
    'wm-btn', variantClass[variant],
    size === 'sm' && 'wm-btn-sm',
    size === 'lg' && 'wm-btn-lg',
    block && 'wm-btn-block',
    className,
  ].filter(Boolean).join(' ');

  if (to) {
    return (
      <Link to={to} className={cls}>
        {children}
      </Link>
    );
  }
  return (
    <button type="button" className={cls} {...rest}>
      {children}
    </button>
  );
}

/* ---------- Badge / Status ---------- */
type StatusTone = 'verified' | 'pending' | 'error' | 'neutral' | 'gold';

const STATUS_TONES: Record<string, StatusTone> = {
  VERIFIED: 'verified', ACTIVE: 'verified', FUNDED: 'verified', RELEASED: 'verified', SIGNED: 'verified',
  PENDING: 'pending', 'PENDING_VERIFICATION': 'pending', CREATED: 'pending', DRAFT: 'pending', REVIEW: 'pending',
  DISPUTED: 'error', CANCELLED: 'error', REFUNDED: 'error', EXPIRED: 'error', UNVERIFIED: 'error',
  LOCKED: 'gold', ESCROW: 'gold',
};

export function WorldStatus({ status, dot = true }: { status: string; dot?: boolean }) {
  const tone = STATUS_TONES[status.toUpperCase().replace(/[\s-]/g, '_')] ?? 'neutral';
  return (
    <span className={`wm-badge wm-badge--${tone}`}>
      {dot && <span className="wm-badge__dot" aria-hidden="true" />}
      {status.replace(/_/g, ' ')}
    </span>
  );
}

export function WorldBadge({
  tone = 'neutral', children,
}: { tone?: StatusTone; children: React.ReactNode }) {
  return <span className={`wm-badge wm-badge--${tone}`}>{children}</span>;
}

/* ---------- Skeletons ---------- */
export function WorldSkeleton({ h = 16, w = '100%', style }: { h?: number; w?: number | string; style?: React.CSSProperties }) {
  return <div className="wm-skeleton" style={{ height: h, width: w, ...style }} aria-hidden="true" />;
}

export function MineralCardSkeleton() {
  return (
    <div className="wm-card">
      <WorldSkeleton h={180} style={{ borderRadius: 0 }} />
      <div className="wm-card__body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <WorldSkeleton h={18} w="70%" />
        <WorldSkeleton h={14} w="45%" />
        <WorldSkeleton h={14} w="55%" />
      </div>
    </div>
  );
}

/* ---------- States ---------- */
export function WorldEmptyState({
  title, hint, action,
}: { title: string; hint?: string; action?: React.ReactNode }) {
  return (
    <div className="wm-state" role="status">
      <div className="wm-state__title">{title}</div>
      {hint && <p style={{ margin: 0, maxWidth: '42ch' }}>{hint}</p>}
      {action}
    </div>
  );
}

export function WorldErrorState({
  title = 'This content could not be loaded',
  detail, onRetry, preserveNote,
}: { title?: string; detail?: string; onRetry?: () => void; preserveNote?: string }) {
  return (
    <div className="wm-state" role="alert" style={{ borderColor: 'rgba(196,67,59,0.4)' }}>
      <div className="wm-state__title">{title}</div>
      {detail && <p style={{ margin: 0, maxWidth: '48ch' }}>{detail}</p>}
      {preserveNote && (
        <p style={{ margin: 0, fontSize: 'var(--text-caption)', color: 'var(--wm-fog)' }}>{preserveNote}</p>
      )}
      {onRetry && (
        <button type="button" className="wm-btn wm-btn-secondary wm-btn-sm" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
