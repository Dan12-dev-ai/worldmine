/**
 * World Mine — Mineral Detail (Phase 5, §18-19).
 * Structure: identity hero → verification → origin/quantity → price → seller →
 * transaction CTAs. Evidence sections render only what the API provides;
 * missing evidence says "not yet available" (§38).
 */
import 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../../shared/api/client';
import type { Listing } from '../../shared/types/domain';
import { WorldButton, WorldErrorState, WorldSkeleton, WorldStatus } from '../../design-system';
import { VerificationBadge } from '../../design-system/patterns/VerificationBadge';

export function MineralDetailPage() {
  const { listingId } = useParams<{ listingId: string }>();

  const { data: listing, isLoading, isError, error, refetch } = useQuery<Listing, Error>({
    queryKey: ['marketplace/listing', listingId],
    queryFn: ({ signal }) => api.get<Listing>(`/api/marketplace/listings/${listingId}`, { signal }),
    retry: 1,
  });

  if (isLoading) return <MineralDetailSkeleton />;
  if (isError || !listing) {
    return (
      <div className="wm-container" style={{ paddingBlock: 'var(--space-9)' }}>
        <WorldErrorState
          title="This mineral could not be found"
          detail={error instanceof Error ? error.message : 'The listing may have been removed or is temporarily unavailable.'}
          onRetry={() => refetch()}
        />
        <div style={{ textAlign: 'center', marginTop: 'var(--space-5)' }}>
          <WorldButton to="/marketplace" variant="secondary">Back to marketplace</WorldButton>
        </div>
      </div>
    );
  }

  return <MineralDetailView listing={listing} />;
}

function MineralDetailSkeleton() {
  return (
    <div className="wm-container" style={{ paddingBlock: 'var(--space-8)' }}>
      <WorldSkeleton h={320} />
      <div style={{ height: 24 }} />
      <div className="wm-grid-12">
        <div style={{ gridColumn: 'span 8' }}><WorldSkeleton h={240} /></div>
        <div style={{ gridColumn: 'span 4' }}><WorldSkeleton h={240} /></div>
      </div>
    </div>
  );
}

function MineralDetailView({ listing }: { listing: Listing }) {
  const origin = [listing.city, listing.country].filter(Boolean).join(', ');
  const price = listing.unit_price ?? listing.total_price;
  const quantity = listing.quantity != null
    ? `${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(listing.quantity)} units`
    : 'Quantity unavailable';

  return (
    <div className="wm-container" style={{ paddingBlock: 'var(--space-6)' }}>
      <nav aria-label="Breadcrumb" style={{ marginBottom: 'var(--space-4)' }}>
        <Link to="/marketplace" style={{ color: 'var(--wm-ash)', fontSize: 'var(--text-small)', textDecoration: 'none' }}>
          ← Marketplace
        </Link>
      </nav>

      <div className="wm-grid-12">
        {/* MAIN COLUMN */}
        <div style={{ gridColumn: 'span 8' }}>
          <div className="wm-mineral-card__media" style={{ borderRadius: 'var(--radius-lg)', aspectRatio: '21/9' }}>
            <span className="wm-mineral-card__glyph">{listing.mineral_type ?? 'MINERAL'}</span>
          </div>

          <div className="wm-surface" style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)', marginTop: 'var(--space-4)' }}>
            <h1 style={{ fontSize: 'var(--text-h1)', marginTop: 0 }}>{listing.title}</h1>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
              <WorldStatus status={listing.status === 'active' ? 'ACTIVE' : 'INACTIVE'} />
              {listing.listing_type && <span className="wm-badge wm-badge--neutral">{listing.listing_type}</span>}
              {listing.quality_grade && <span className="wm-badge wm-badge--gold">Grade {listing.quality_grade}</span>}
            </div>
            {listing.description && (
              <p style={{ color: 'var(--wm-fog)', marginTop: 'var(--space-4)', lineHeight: 1.7 }}>{listing.description}</p>
            )}
          </div>

          {/* SPECIFICATIONS */}
          <section className="wm-surface" style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)', marginTop: 'var(--space-4)' }} aria-labelledby="spec-heading">
            <h2 id="spec-heading" style={{ fontSize: 'var(--text-h3)', marginTop: 0 }}>Specifications</h2>
            <dl className="wm-kv">
              <div><dt>Mineral</dt><dd>{listing.mineral_type ?? 'Not specified'}</dd></div>
              <div><dt>Origin</dt><dd>{origin || 'Not declared'}</dd></div>
              <div><dt>Quantity</dt><dd className="wm-mono">{quantity}</dd></div>
              <div><dt>Listed</dt><dd>{listing.created_at ? new Date(listing.created_at).toLocaleDateString() : '—'}</dd></div>
              {listing.latitude != null && listing.longitude != null && (
                <div><dt>GPS</dt><dd className="wm-mono">{listing.latitude.toFixed(3)}°, {listing.longitude.toFixed(3)}°</dd></div>
              )}
            </dl>
          </section>

          {/* EVIDENCE */}
          <section className="wm-surface" style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)', marginTop: 'var(--space-4)' }} aria-labelledby="evidence-heading">
            <h2 id="evidence-heading" style={{ fontSize: 'var(--text-h3)', marginTop: 0 }}>Verification & evidence</h2>
            <VerificationBadge state="PENDING" detail="Verification pipeline for this listing has not completed yet." />
            <p style={{ fontSize: 'var(--text-small)', color: 'var(--wm-fog)' }}>
              Assay documents, inspection reports and origin evidence appear here as they are
              attached by the seller and verified. Evidence is not yet available for this listing.
            </p>
          </section>
        </div>

        {/* SIDEBAR */}
        <aside style={{ gridColumn: 'span 4' }}>
          <div className="wm-surface" style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)', position: 'sticky', top: 88 }}>
            <div className="wm-mineral-card__price" style={{ fontSize: 'var(--text-h2)' }}>
              {price != null ? `$${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(price)}${listing.unit_price != null ? ' / unit' : ''}` : 'Quote on request'}
            </div>
            <dl className="wm-kv" style={{ marginBlock: 'var(--space-4)' }}>
              <div><dt>Availability</dt><dd>{listing.status === 'active' ? 'Available' : 'Unavailable'}</dd></div>
              <div><dt>Seller</dt><dd className="wm-mono">{listing.seller_id.slice(0, 8)}…</dd></div>
            </dl>
            <div style={{ display: 'grid', gap: 10 }}>
              <WorldButton block>Request connection</WorldButton>
              <WorldButton variant="secondary" block>Request video meeting</WorldButton>
              <p style={{ margin: 0, fontSize: 'var(--text-caption)', color: 'var(--wm-ash)', textAlign: 'center' }}>
                Negotiations move into a secure deal room with escrow protection.
              </p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
