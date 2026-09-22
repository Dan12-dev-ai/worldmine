/**
 * World Mine — Marketplace (Phase 5, v2).
 * 12-column grid, persistent URL filters, functional filter system.
 * Server-side filtering not implemented yet — filters applied client-side
 * but query params ARE sent so backend can adopt without changes.
 */
import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../../shared/api/client';
import type { Listing } from '../../shared/types/domain';
import {
  MineralCard, MineralCardSkeleton, WorldEmptyState, WorldErrorState,
  WorldButton, WorldBadge,
} from '../../design-system';

const VIEWS = ['grid', 'list'] as const;
type View = (typeof VIEWS)[number];

export function MarketplacePage() {
  const [params, setParams] = useSearchParams();
  const view = (params.get('view') as View) ?? 'grid';
  const q = params.get('q') ?? '';
  const type = params.get('type') ?? '';
  const country = params.get('country') ?? '';
  const grade = params.get('grade') ?? '';
  const status = params.get('status') ?? 'active';
  const [savedSearch, setSavedSearch] = useState<string | null>(null);

  const { data: listings, isLoading, isError, refetch } = useQuery<Listing[], Error>({
    queryKey: 'marketplace/listings',
    queryFn: async ({ signal }) => {
      const query = params.toString();
      const suffix = query ? `?${query}` : '';
      const raw = await api.get<Listing[]>(`/api/marketplace/listings${suffix}`, { signal });
      return Array.isArray(raw) ? raw : [];
    },
    staleTime: 60_000,
    retry: 1,
  });

  const setParam = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value); else next.delete(key);
    setParams(next, { replace: true });
  };

  const hasFilters = q || type || country || grade || (status && status !== 'active');

  const filtered = useMemo(() => {
    let out = listings ?? [];
    if (status && status !== 'all') out = out.filter((l) => l.status === status);
    if (type) out = out.filter((l) => (l.mineral_type ?? '').toLowerCase().includes(type.toLowerCase()));
    if (country) out = out.filter((l) => (l.country ?? '').toLowerCase() === country.toLowerCase());
    if (grade) out = out.filter((l) => (l.quality_grade ?? '').toLowerCase() === grade.toLowerCase());
    if (q) {
      const needle = q.toLowerCase();
      out = out.filter((l) =>
        [l.title, l.description, l.mineral_type, l.country, l.city, l.id, l.seller_id]
          .some((f) => (f ?? '').toString().toLowerCase().includes(needle)));
    }
    return out;
  }, [listings, q, type, country, grade, status]);

  const facets = useMemo(() => {
    const all = listings ?? [];
    const uniq = (xs: (string | null | undefined)[]) =>
      Array.from(new Set(xs.filter((x): x is string => Boolean(x)))).sort();
    return {
      types: uniq(all.map((l) => l.mineral_type)),
      countries: uniq(all.map((l) => l.country)),
      grades: uniq(all.map((l) => l.quality_grade)),
    };
  }, [listings]);

  function saveSearch() {
    const current = params.toString() || 'all';
    try {
      localStorage.setItem('wm.saved-search', current);
      setSavedSearch(current);
    } catch { /* storage unavailable */ }
  }

  function clearFilters() { setParams(new URLSearchParams()); }

  return (
    <div className="wm-container" style={{ padding: 'var(--space-6) var(--gutter) var(--space-8)' }}>
      {/* ── Header ── */}
      <div className="wm-section__head wm-section__head--row" style={{ marginBottom: 'var(--space-5)' }}>
        <div>
          <span className="wm-kicker">Mineral marketplace</span>
          <h1 style={{ fontSize: 'var(--text-h1)', marginTop: 'var(--space-2)' }}>
            Browse verified minerals
          </h1>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
          {(['grid', 'list'] as const).map((v) => (
            <button
              key={v}
              type="button"
              className={`wm-btn wm-btn-sm ${view === v ? 'wm-btn-primary' : 'wm-btn-ghost'}`}
              onClick={() => setParam('view', v)}
            >
              {v === 'grid' ? 'Grid' : 'List'}
            </button>
          ))}
          <WorldButton variant="ghost" size="sm" onClick={saveSearch}>Save search</WorldButton>
          {savedSearch && <WorldBadge tone="gold">Saved</WorldBadge>}
        </div>
      </div>

      {/* ── Filters ── */}
      <div
        className="wm-surface"
        style={{ padding: 'var(--space-4)', marginBottom: 'var(--space-5)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-4)', alignItems: 'flex-end' }}
      >
        <FilterSelect label="Mineral type" value={type} options={facets.types} onChange={(v) => setParam('type', v)} />
        <FilterSelect label="Country" value={country} options={facets.countries} onChange={(v) => setParam('country', v)} />
        <FilterSelect label="Grade" value={grade} options={facets.grades} onChange={(v) => setParam('grade', v)} />
        <FilterSelect
          label="Status" value={status} options={['active', 'inactive', 'all']}
          labels={{ active: 'Available', inactive: 'Unavailable', all: 'All' }}
          onChange={(v) => setParam('status', v)}
        />
        <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap' }}>
          {hasFilters && (
            <button type="button" className="wm-btn wm-btn-ghost wm-btn-sm" onClick={clearFilters}>
              Clear filters
            </button>
          )}
          {q && (
            <span className="wm-mono" style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-fog)' }}>
              Search: {q}
            </span>
          )}
        </div>
      </div>

      {/* ── Results count ── */}
      {!isLoading && !isError && filtered.length > 0 && (
        <p
          className="wm-mono"
          style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-ash)', marginBottom: 'var(--space-4)' }}
          aria-live="polite"
        >
          {filtered.length} {filtered.length === 1 ? 'mineral' : 'minerals'} found
          {hasFilters && <>{status === 'active' ? '' : `· ${status}`}</>}
        </p>
      )}

      {/* ── Loading skeleton ── */}
      {isLoading && (
        <div className="wm-cols wm-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i}><MineralCardSkeleton /></div>
          ))}
        </div>
      )}

      {/* ── Error state ── */}
      {isError && (
        <WorldErrorState
          title="The marketplace could not be reached"
          detail="Your filters and search terms are preserved. Nothing was lost."
          onRetry={() => refetch()}
        />
      )}

      {/* ── Empty state — filters matched nothing */}
      {!isLoading && !isError && filtered.length === 0 && (
        <WorldEmptyState
          title="No minerals match these filters"
          hint="Try widening your filters — or save this search and get notified when a matching mineral is listed."
          action={<WorldButton variant="secondary" size="sm" onClick={clearFilters}>Clear filters</WorldButton>}
        />
      )}

      {/* ── Results grid ── */}
      {!isLoading && !isError && filtered.length > 0 && (
        <div
          className={view === 'list' ? 'wm-cols wm-cols-1' : 'wm-cols wm-cols-3'}
          style={view === 'list' ? { gridTemplateColumns: '1fr', gap: 12 } : undefined}
        >
          {filtered.map((l) => (
            <div key={l.id}>
              <MineralCard listing={l} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function FilterSelect({
  label, value, options, labels, onChange,
}: {
  label: string; value: string; options: string[];
  labels?: Record<string, string>; onChange: (v: string) => void;
}) {
  return (
    <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 'var(--text-caption)', color: 'var(--wm-ash)' }}>
      {label}
      <select
        className="wm-input"
        style={{ padding: '6px 10px', width: 'auto', minWidth: 130, fontSize: 'var(--text-small)' }}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>{labels?.[o] ?? o}</option>
        ))}
      </select>
    </label>
  );
}
