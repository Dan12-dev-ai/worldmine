/**
 * World Mine — MineralCard (Phase 5 domain component).
 * Critical info first: mineral, origin, grade, quantity, verification, seller,
 * availability, price. One primary CTA. Never overloaded (§17).
 */
import 'react';
import { Link } from 'react-router-dom';
import type { Listing } from '../../shared/types/domain';
import { WorldStatus } from '../primitives';

function formatPrice(listing: Listing): string {
  // Never fabricate: when price is absent the card says so (§38).
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
        <div className="wm-mineral-card__media">
          <span className="wm-mineral-card__glyph">{listing.mineral_type ?? 'UNSPECIFIED MINERAL'}</span>
          {listing.status !== 'active' && (
            <span style={{ position: 'absolute', top: 12, right: 12 }}>
              <WorldStatus status="INACTIVE" />
            </span>
          )}
        </div>
        <div className="wm-card__body">
          <h3 style={{ fontSize: 'var(--text-h3)', marginBottom: 4, display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
            {listing.title}
          </h3>
          <p style={{ margin: 0, fontSize: 'var(--text-caption)', color: 'var(--wm-ash)', fontFamily: 'var(--font-mono)' }}>
            {origin}
          </p>

          <div className="wm-mineral-card__meta">
            {listing.quality_grade && (
              <span className="wm-mineral-card__meta-item">Grade {listing.quality_grade}</span>
            )}
            <span className="wm-mineral-card__meta-item">{formatQuantity(listing)}</span>
            <span className="wm-mineral-card__meta-item">{listing.listing_type ?? 'fixed price'}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 'var(--space-4)' }}>
            <span className="wm-mineral-card__price">{formatPrice(listing)}</span>
            <span className="wm-badge wm-badge--neutral">
              <span className="wm-badge__dot" aria-hidden="true" />
              {listing.status === 'active' ? 'Available' : 'Unavailable'}
            </span>
          </div>
        </div>
      </Link>
    </article>
  );
}
