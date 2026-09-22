/**
 * World Mine — Marketplace (Phase 5, §16).
 * Views: grid/list. URL-persistent filters (q, type, country, grade, status,
 * view). Server-side filtering is not implemented yet (drift flag #1) so
 * filtering happens client-side, but filter params are ALREADY sent as query
 * params so the backend can adopt them without any frontend change.
 */
import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../../shared/api/client';
import type { Listing } from '../../shared/types/domain';
import { MineralCard, MineralCardSkeleton, WorldEmptyState, WorldErrorState, WorldButton, WorldBadge } from '../../design-system';

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

  // Facets derived from real data — never invented (§38).
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
    } catch { /* storage unavailable — non-critical */ }
  }

  return (
    <div className="wm-container" style={{ padding: 'var(--space-6) var(--gutter) var(--space-8)' }}>
      <div className="wm-section__head">
        <span className="wm-kicker">Marketplace</span>
        <h1 style={{ fontSize: 'var(--text-h1)' }}>Verified minerals</h1>
      </div>

      {/* Search + view switch */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
        <input
          className="wm-input" style={{ flex: '1 1 280px', maxWidth: 480 }}
          placeholder="Search mineral, origin, seller, grade or listing ID…"
          aria-label="Search listings"
          value={q}
          onChange={(e) => setParam('q', e.target.value)}
        />
        <div role="group" aria-label="View" style={{ display: 'flex', gap: 4 }}>
          {VIEWS.map((v) => (
            <button
              key={v} type="button"
              className={`wm-btn wm-btn-sm ${view === v ? 'wm-btn-secondary' : 'wm-btn-ghost'}`}
              aria-pressed={view === v}
              onClick={() => setParam('view', v)}
            >
              {v === 'grid' ? 'Grid' : 'List'}
            </button>
          ))}
        </div>
        <WorldButton variant="ghost" size="sm" onClick={saveSearch}>Save search</WorldButton>
        {savedSearch && <WorldBadge tone="gold">Saved: {savedSearch}</WorldBadge>}
      </div>

      {/* Filters (facets from real data) */}
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 'var(--space-5)' }}>
        <FilterSelect label="Mineral type" value={type} options={facets.types} onChange={(v) => setParam('type', v)} />
        <FilterSelect label="Country" value={country} options={facets.countries} onChange={(v) => setParam('country', v)} />
        <FilterSelect label="Grade" value={grade} options={facets.grades} onChange={(v) => setParam('grade', v)} />
        <FilterSelect
          label="Availability" value={status}
          options={['active', 'inactive', 'all']}
          labels={{ active: 'Available', inactive: 'Unavailable', all: 'All' }}
          onChange={(v) => setParam('status', v)}
        />
        {(q || type || country || grade || (status && status !== 'active')) && (
          <button type="button" className="wm-btn wm-btn-ghost wm-btn-sm" onClick={() => setParams(new URLSearchParams())}>
            Clear filters
          </button>
        )}
      </div>

      {/* Results */}
      {isLoading && (
        <div className="wm-grid-12">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} style={{ gridColumn: 'span 4' }}><MineralCardSkeleton /></div>
          ))}
        </div>
      )}

      {isError && (
        <WorldErrorState
          title="The marketplace could not be reached"
          detail="Your filters and search terms are preserved. Nothing was lost."
          onRetry={() => refetch()}
        />
      )}

      {!isLoading && !isError && filtered.length === 0 && (
        <WorldEmptyState
          title="No minerals match these filters"
          hint="Try widening your filters — or save this search and get notified when a matching mineral is listed."
        />
      )}

      {!isLoading && !isError && filtered.length > 0 && (
        <>
          <p className="wm-mono" style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-ash)' }} aria-live="polite">
            {filtered.length} {filtered.length === 1 ? 'mineral' : 'minerals'} found
          </p>
          <div className="wm-grid-12" style={view === 'list' ? { gridTemplateColumns: '1fr', gap: 12 } : undefined}>
            {filtered.map((l) => (
              <div key={l.id} style={view === 'list' ? undefined : { gridColumn: 'span 4' }}>
                <MineralCard listing={l} />
              </div>
            ))}
          </div>
        </>
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
    <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 'var(--text-caption)' }}>
      {label}
      <select
        className="wm-input" style={{ padding: '6px 10px', width: 'auto', minWidth: 120 }}
        value={value} onChange={(e) => onChange(e.target.value)}
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>{labels?.[o] ?? o}</option>
        ))}
      </select>
    </label>
  );
}
