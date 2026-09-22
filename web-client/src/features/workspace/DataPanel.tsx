/**
 * World Mine — data panel + stat grid (workspace modules, Phase 6–9).
 *
 * Single place that decides how a list request looks while loading, when it
 * fails, when the payload shape is wrong, and when it legitimately returns
 * nothing. Modules therefore cannot accidentally render a fake empty table or
 * a spinner that hides an error (§38/§47).
 */
import { useMemo } from 'react';
import type { ReactNode } from 'react';
import { WorldEmptyState, WorldErrorState, WorldSkeleton } from '../../design-system';

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  align?: 'left' | 'right';
  nowrap?: boolean;
}

export interface DataPanelProps<T> {
  title: string;
  description?: string;
  /** `null` = not loaded / failed / wrong shape; `[]` = genuinely empty. */
  rows: T[] | null;
  columns: Column<T>[];
  rowKey: (row: T, index: number) => string;
  isLoading: boolean;
  isError: boolean;
  errorDetail?: string;
  onRetry?: () => void;
  emptyTitle: string;
  emptyHint?: string;
  caption?: string;
  actions?: ReactNode;
  /** Rendered under the table when rows exist (e.g. a detail pane). */
  children?: ReactNode;
  /** Show only the first N records but report the true total. */
  limitedTo?: number;
}

export function DataPanel<T>({
  title, description, rows, columns, rowKey, isLoading, isError, errorDetail,
  onRetry, emptyTitle, emptyHint, caption, actions, children, limitedTo,
}: DataPanelProps<T>) {
  const visible = useMemo(
    () => (rows && limitedTo ? rows.slice(0, limitedTo) : rows ?? []),
    [rows, limitedTo],
  );
  const total = rows?.length ?? 0;

  return (
    <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
      <header
        style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          gap: 'var(--space-4)', flexWrap: 'wrap', marginBottom: 'var(--space-4)',
        }}
      >
        <div>
          <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>{title}</h2>
          {description && <p className="wm-hint" style={{ margin: '4px 0 0', maxWidth: '70ch' }}>{description}</p>}
        </div>
        {actions}
      </header>

      {isLoading && (
        <div style={{ display: 'grid', gap: 8 }} role="status" aria-live="polite">
          <span className="wm-sr-only">Loading {title}</span>
          {[0, 1, 2, 3].map((i) => <WorldSkeleton key={i} h={38} />)}
        </div>
      )}

      {!isLoading && isError && (
        <WorldErrorState
          title={`${title} could not be loaded`}
          detail={errorDetail}
          onRetry={onRetry}
          preserveNote="No stand-in data is shown — the failure is reported instead of hidden (§47)."
        />
      )}

      {!isLoading && !isError && rows === null && (
        <WorldErrorState
          title={`${title} returned an unexpected shape`}
          detail="The response was neither a JSON array nor a { data: [...] } envelope, so it cannot be displayed."
          onRetry={onRetry}
        />
      )}

      {!isLoading && !isError && rows !== null && total === 0 && (
        <WorldEmptyState title={emptyTitle} hint={emptyHint} />
      )}

      {!isLoading && !isError && total > 0 && (
        <>
          <div style={{ overflowX: 'auto' }}>
            <table className="wm-table">
              <caption className="wm-sr-only">{caption ?? title}</caption>
              <thead>
                <tr>
                  {columns.map((c) => (
                    <th key={c.key} scope="col" style={{ textAlign: c.align === 'right' ? 'right' : 'left' }}>
                      {c.header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {visible.map((row, index) => (
                  <tr key={rowKey(row, index)}>
                    {columns.map((c) => (
                      <td
                        key={c.key}
                        style={{
                          textAlign: c.align === 'right' ? 'right' : 'left',
                          whiteSpace: c.nowrap ? 'nowrap' : undefined,
                        }}
                      >
                        {c.render(row)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {limitedTo != null && total > limitedTo && (
            <p className="wm-hint" style={{ marginTop: 10 }}>
              Showing the first {limitedTo} of {total} records returned by the API.
            </p>
          )}
          {children}
        </>
      )}
    </section>
  );
}

export interface StatItem {
  label: string;
  value: string;
  tone?: 'default' | 'gold' | 'verified' | 'warning';
}

const STAT_TONE: Record<NonNullable<StatItem['tone']>, string> = {
  default: 'var(--wm-porcelain)',
  gold: 'var(--wm-gold-soft)',
  verified: 'var(--wm-verified)',
  warning: 'var(--wm-warning)',
};

/** Compact metric row. Values are pre-formatted by the caller (already honest). */
export function StatGrid({ items, title }: { items: StatItem[]; title?: string }) {
  return (
    <section>
      {title && <h2 style={{ fontSize: 'var(--text-h3)', marginBottom: 'var(--space-3)' }}>{title}</h2>}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 'var(--space-4)' }}>
        {items.map((item) => (
          <div key={item.label} className="wm-card" style={{ padding: 'var(--space-4)' }}>
            <div className="wm-label">{item.label}</div>
            <div
              className="wm-mono"
              style={{ fontSize: 'var(--text-h3)', color: STAT_TONE[item.tone ?? 'default'], marginTop: 6 }}
            >
              {item.value}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
