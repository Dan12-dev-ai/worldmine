/**
 * World Mine — Mineral Detail (Phase 5, §18/§19).
 * Identity → verification → specifications → origin → seller → transaction panel.
 * Verification is explicit: who/when/what/evidence — or an honest "no data".
 * CTAs guide to connection without faking backend capabilities (§47).
 */
import { useState } from "react";
import { Link, useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../../shared/api/client';
import type { Listing } from '../../shared/types/domain';
import {
  WorldButton, WorldErrorState, WorldSkeleton, WorldBadge,
} from '../../design-system';
import { VerificationBadge } from '../../design-system/patterns/VerificationBadge';
import { LifecycleStepper } from '../../design-system/patterns/LifecycleStepper';

export function MineralDetailPage() {
  const { listingId = '' } = useParams();
  const { data: listing, isLoading, isError } = useQuery<Listing, Error>({
    queryKey: ['listing', listingId],
    queryFn: ({ signal }) => api.get<Listing>(`/api/marketplace/listings/${listingId}`, { signal }),
    staleTime: 60_000,
    retry: 1,
  });

  if (isLoading) {
    return (
      <div className="wm-container" style={{ padding: 'var(--space-7) var(--gutter)' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,7fr) minmax(0,5fr)', gap: 'var(--space-6)' }}>
          <WorldSkeleton h={420} />
          <WorldSkeleton h={420} />
        </div>
      </div>
    );
  }

  if (isError || !listing) {
    return (
      <div className="wm-container" style={{ padding: 'var(--space-8) var(--gutter)' }}>
        <WorldErrorState
          title="This mineral could not be loaded"
          detail="The listing may have been withdrawn, or the link is incorrect."
          onRetry={() => window.location.reload()}
        />
        <p style={{ textAlign: 'center', marginTop: 'var(--space-4)' }}>
          <Link to="/marketplace" style={{ color: 'var(--wm-gold-soft)' }}>← Back to marketplace</Link>
        </p>
      </div>
    );
  }

  return <MineralDetail listing={listing} />;
}

function MineralDetail({ listing }: { listing: Listing }) {
  const [watched, setWatched] = useState<boolean>(() => {
    try { return localStorage.getItem(`wm.watch.${listing.id}`) === '1'; } catch { return false; }
  });
  const [shared, setShared] = useState(false);

  const toggleWatch = () => {
    try {
      if (watched) localStorage.removeItem(`wm.watch.${listing.id}`);
      else localStorage.setItem(`wm.watch.${listing.id}`, '1');
      setWatched(!watched);
    } catch { /* storage unavailable */ }
  };

  const share = async () => {
    const url = window.location.href;
    try {
      if (navigator.share) await navigator.share({ title: listing.title, url });
      else await navigator.clipboard.writeText(url);
      setShared(true);
      window.setTimeout(() => setShared(false), 2000);
    } catch { /* user cancelled */ }
  };

  const verification = listing.verification ?? null;
  const origin = [listing.city, listing.country].filter(Boolean).join(', ') || 'Not declared';
  const coords = listing.latitude != null && listing.longitude != null
    ? `${listing.latitude.toFixed(4)}°, ${listing.longitude.toFixed(4)}°`
    : null;

  return (
    <article className="wm-container" style={{ padding: 'var(--space-6) var(--gutter) var(--space-8)' }}>
      <nav aria-label="Breadcrumb" style={{ marginBottom: 'var(--space-4)', fontSize: 'var(--text-caption)' }}>
        <Link to="/marketplace" style={{ color: 'var(--wm-ash)' }}>Marketplace</Link>
        <span aria-hidden="true"> / </span>
        <span style={{ color: 'var(--wm-fog)' }}>{listing.title}</span>
      </nav>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 7fr) minmax(0, 5fr)', gap: 'var(--space-6)' }}>
        {/* LEFT — identity + evidence */}
        <div style={{ display: 'grid', gap: 'var(--space-5)', alignContent: 'start' }}>
          <div className="wm-card" style={{ overflow: 'hidden' }}>
            <div className="wm-mineral-card__media" style={{ aspectRatio: '16/7' }}>
              <span className="wm-mineral-card__glyph">{listing.mineral_type ?? 'MINERAL'}</span>
            </div>
            <div className="wm-card__body">
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12, flexWrap: 'wrap' }}>
                <div>
                  <h1 style={{ fontSize: 'var(--text-h1)', marginBottom: 4 }}>{listing.title}</h1>
                  <p className="wm-mono" style={{ margin: 0, fontSize: 'var(--text-caption)', color: 'var(--wm-ash)' }}>
                    ID {listing.id.slice(0, 8)} · Listed {listing.created_at ? new Date(listing.created_at).toLocaleDateString() : 'date unavailable'}
                  </p>
                </div>
                <VerificationBadge state={verification?.state ?? 'UNVERIFIED'} />
              </div>
              {listing.description && (
                <p style={{ marginTop: 'var(--space-4)', color: 'var(--wm-fog)', maxWidth: '70ch' }}>{listing.description}</p>
              )}
            </div>
          </div>

          {/* Verification — explicit, §19 */}
          <section className="wm-surface" style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)' }} aria-labelledby="verif-h">
            <h2 id="verif-h" style={{ fontSize: 'var(--text-h3)', marginBottom: 10 }}>Verification</h2>
            {verification ? (
              <dl style={{ margin: 0, display: 'grid', gridTemplateColumns: 'max-content 1fr', gap: '6px 18px', fontSize: 'var(--text-small)' }}>
                <dt style={{ color: 'var(--wm-ash)' }}>State</dt>
                <dd style={{ margin: 0 }}><VerificationBadge state={verification.state} /></dd>
                <dt style={{ color: 'var(--wm-ash)' }}>Verified by</dt>
                <dd style={{ margin: 0 }}>{verification.verified_by ?? 'Not recorded'}</dd>
                <dt style={{ color: 'var(--wm-ash)' }}>When</dt>
                <dd style={{ margin: 0 }}>{verification.verified_at ? new Date(verification.verified_at).toLocaleString() : 'Not recorded'}</dd>
                <dt style={{ color: 'var(--wm-ash)' }}>What was verified</dt>
                <dd style={{ margin: 0 }}>{verification.what?.join(', ') ?? 'Scope not recorded'}</dd>
                <dt style={{ color: 'var(--wm-ash)' }}>Evidence</dt>
                <dd style={{ margin: 0 }}>{verification.evidence_count ?? 0} document(s)</dd>
                <dt style={{ color: 'var(--wm-ash)' }}>Expires</dt>
                <dd style={{ margin: 0 }}>{verification.expires_at ? new Date(verification.expires_at).toLocaleDateString() : 'No expiry recorded'}</dd>
              </dl>
            ) : (
              <p style={{ margin: 0, color: 'var(--wm-fog)', fontSize: 'var(--text-small)' }}>
                No verification has been submitted for this listing yet. Treat all claims as
                unverified until evidence is exchanged with the seller inside a deal room.
              </p>
            )}
          </section>

          {/* Specifications + Origin */}
          <section className="wm-surface" style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)' }} aria-labelledby="spec-h">
            <h2 id="spec-h" style={{ fontSize: 'var(--text-h3)', marginBottom: 10 }}>Specifications & origin</h2>
            <dl style={{ margin: 0, display: 'grid', gridTemplateColumns: 'max-content 1fr', gap: '6px 18px', fontSize: 'var(--text-small)' }}>
              <dt style={{ color: 'var(--wm-ash)' }}>Mineral</dt><dd style={{ margin: 0 }}>{listing.mineral_type ?? 'Not declared'}</dd>
              <dt style={{ color: 'var(--wm-ash)' }}>Quality grade</dt><dd style={{ margin: 0 }}>{listing.quality_grade ?? 'Not declared'}</dd>
              <dt style={{ color: 'var(--wm-ash)' }}>Quantity</dt>
              <dd style={{ margin: 0 }}>
                {listing.quantity != null
                  ? `${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(listing.quantity)} units`
                  : 'Not declared'}
              </dd>
              <dt style={{ color: 'var(--wm-ash)' }}>Listing type</dt><dd style={{ margin: 0 }}>{listing.listing_type ?? 'fixed price'}</dd>
              <dt style={{ color: 'var(--wm-ash)' }}>Origin</dt><dd style={{ margin: 0 }}>{origin}</dd>
              {coords && (
                <>
                  <dt style={{ color: 'var(--wm-ash)' }}>Coordinates</dt>
                  <dd style={{ margin: 0 }} className="wm-mono">{coords}</dd>
                </>
              )}
              <dt style={{ color: 'var(--wm-ash)' }}>Last updated</dt>
              <dd style={{ margin: 0 }}>{listing.updated_at ? new Date(listing.updated_at).toLocaleDateString() : 'Unavailable'}</dd>
            </dl>
          </section>

          <div aria-label="Transaction lifecycle"><LifecycleStepper /></div>
        </div>

        {/* RIGHT — transaction panel */}
        <aside style={{ display: 'grid', gap: 'var(--space-5)', alignContent: 'start' }}>
          <div className="wm-surface" style={{ padding: 'var(--space-5)', borderRadius: 'var(--radius-lg)', position: 'sticky', top: 88 }}>
            <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
              <span className="wm-mineral-card__price" style={{ fontSize: '1.375rem' }}>
                {listing.unit_price != null
                  ? `$${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(listing.unit_price)} / unit`
                  : listing.total_price != null
                    ? `$${new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(listing.total_price)}`
                    : 'Quote on request'}
              </span>
              <WorldBadge tone={listing.status === 'active' ? 'verified' : 'neutral'}>
                {listing.status === 'active' ? 'Available' : 'Unavailable'}
              </WorldBadge>
            </div>

            <div style={{ margin: 'var(--space-4) 0', borderTop: 'var(--border-hairline)' }} />

            <h2 style={{ fontSize: 'var(--text-h3)', marginBottom: 6 }}>Seller</h2>
            <p style={{ margin: 0, fontSize: 'var(--text-small)', color: 'var(--wm-fog)' }}>
              {listing.seller?.username ?? `Seller ${listing.seller_id.slice(0, 8)}`}
              {' · '}
              {listing.seller?.verification_level
                ? `Verification: ${listing.seller.verification_level}`
                : 'Verification: unknown'}
            </p>

            <div style={{ display: 'grid', gap: 10, marginTop: 'var(--space-5)' }}>
              <WorldButton to={`/login?next=/marketplace/${listing.id}`} block>
                Connect with this seller
              </WorldButton>
              <p style={{ margin: 0, fontSize: 'var(--text-caption)', color: 'var(--wm-ash)' }}>
                Connection opens a secure deal room — video, chat, documents, offers,
                contract and escrow in one place. Both parties must be verified.
              </p>
              <div style={{ display: 'flex', gap: 8 }}>
                <button type="button" className="wm-btn wm-btn-ghost wm-btn-sm" onClick={toggleWatch} aria-pressed={watched}>
                  {watched ? '★ Watching' : '☆ Watch'}
                </button>
                <button type="button" className="wm-btn wm-btn-ghost wm-btn-sm" onClick={share}>
                  {shared ? 'Link copied ✓' : 'Share'}
                </button>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </article>
  );
}
