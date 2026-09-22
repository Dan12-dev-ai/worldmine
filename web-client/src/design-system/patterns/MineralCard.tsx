/**
 * World Mine — MineralCard (Phase 5 domain component, v2).
 * Critical info first: mineral, origin, grade, quantity, verification, seller,
 * availability, price. One primary CTA. Never overloaded (§17).
 *
 * Hierarchy:
 *  1. Media / mineral visual  — top, fixed ratio
 *  2. Mineral name           — H3, display font
 *  3. Origin                 — mono, secondary
 *  4. Grade / quantity       — compact meta chips
 *  5. Price                  — gold mono, dominant
 *  6. Availability badge     — right-aligned
 */
import 'react';
import { Link } from 'react-router-dom';
import type { Listing } from '../../shared/types/domain';
import { WorldStatus } from '../primitives';

function formatPrice(listing: Listing): string {
  const price = listing.unit_price ?? listing.total_price;
  if (price == null) return 'Price on request';
  const amount = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(price);
  return listing.unit_price != null ? `$${amount} / unit` : `$${amount}`;
}

function formatQuantity(listing: Listing): string {
  if (listing.quantity == null) return 'Quantity unavailable';
  return `${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(listing.quantity)} units`;
}

export function MineralCard({ listing }: { listing: Listing }) {
  const origin = [listing.city, listing.country].filter(Boolean).join(', ') || 'Origin not declared';

  return (
    <article className="wm-card wm-card--interactive" data-testid="mineral-card">
      <Link to={`/marketplace/${listing.id}`} style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
        {/* ── Media ── */}
        <div className="wm-mineral-card__media">
          <span className="wm-mineral-card__glyph">
            {listing.mineral_type ?? 'UNSPECIFIED MINERAL'}
          </span>
          {listing.status !== 'active' && (
            <span style={{ position: 'absolute', top: 10, right: 10 }}>
              <WorldStatus status={listing.status} />
            </span>
          )}
        </div>

        {/* ── Body ── */}
        <div className="wm-card__body" style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {/* Name */}
          <h3
            style={{
              fontSize: 'var(--text-h3)',
              fontFamily: 'var(--font-display)',
              fontWeight: 550,
              marginBottom: 2,
              lineHeight: 1.2,
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
            }}
          >
            {listing.title}
          </h3>

          {/* Origin */}
          <p style={{ margin: 0, fontSize: 'var(--text-caption)', color: 'var(--wm-ash)', fontFamily: 'var(--font-mono)', letterSpacing: '0.04em' }}>
            {origin}
          </p>

          {/* Meta chips */}
          {(listing.quality_grade || listing.quantity != null || listing.listing_type) ? (
            <div className="wm-mineral-card__meta" style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {listing.quality_grade && (
                <span className="wm-mineral-card__meta-item">Grade {listing.quality_grade}</span>
              )}
              {listing.quantity != null && (
                <span className="wm-mineral-card__meta-item">{formatQuantity(listing)}</span>
              )}
              {listing.listing_type && (
                <span className="wm-mineral-card__meta-item">{listing.listing_type}</span>
              )}
              {listing.status === 'active' && (
                <span className="wm-mineral-card__meta-item" style={{ color: 'var(--wm-verified)', borderColor: 'var(--wm-verified-line)', backgroundColor: 'var(--wm-verified-bg)' }}>
                  Available
                </span>
              )}
            </div>
          ) : (
            <p className="wm-hint" style={{ fontSize: 'var(--text-caption)' }}>Details not yet available.</p>
          )}

          {/* Footer: price + availability */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'auto', paddingTop: 6 }}>
            <span className="wm-mineral-card__price">{formatPrice(listing)}</span>
            <WorldStatus status={listing.status.toUpperCase()} />
          </div>
        </div>
      </Link>
    </article>
  );
}
