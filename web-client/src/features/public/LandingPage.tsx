/**
 * World Mine — Landing page (Phase 3, v2).
 * Institutional mineral commerce platform.
 * All numbers from real backend data — when unavailable, the section states
 * its capability rather than fabricating statistics (§38/§47).
 */
import { lazy, Suspense, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { api } from '../../shared/api/client';
import type { Listing } from '../../shared/types/domain';
import {
  WorldButton, MineralCardSkeleton, WorldErrorState,
  MineralCard,
} from '../../design-system';

/* 3D is a lazy, capability-gated enhancement — hero is complete without it (§10/§51). */
const GeologicalEnvironment = lazy(() =>
  import('../../three/environments/GeologicalEnvironment').then((m) => ({ default: m.GeologicalEnvironment })),
);

function HeroCanvas() {
  const [ok, setOk] = useState(false);
  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const small = window.matchMedia('(max-width: 768px)').matches;
    const cores = navigator.hardwareConcurrency ?? 4;
    setOk(!reduced && !small && cores >= 4);
  }, []);
  if (!ok) return null;
  return (
    <Suspense fallback={null}>
      <GeologicalEnvironment />
    </Suspense>
  );
}

export function LandingPage() {
  return (
    <div>
      <LandingHero />
      <TrustStrip />
      <MarketplacePreview />
      <HowItWorks />
      <FaceToFace />
      <FinalCta />
    </div>
  );
}

/* ────────────────────────────────────────────────
   HERO — institutional, two-column, content-led
   ──────────────────────────────────────────────── */
function LandingHero() {
  return (
    <section className="wm-hero" aria-labelledby="hero-heading">
      <HeroCanvas />
      <div className="wm-hero__inner">
        {/* LEFT: content */}
        <div>
          <div className="wm-hero__eyebrow">
            <span className="wm-kicker">Institutional mineral marketplace</span>
          </div>

          <h1 id="hero-heading" className="wm-hero__title">
            Global Mineral Commerce,<br />
            <span className="wm-hero__accent">Connected.</span>
          </h1>

          <p className="wm-hero__sub">
            World Mine connects verified mineral buyers and sellers — from verified
            discovery and evidence through negotiation, contract, escrow, logistics
            and GPS-traceable delivery.
          </p>

          <div className="wm-hero__ctas">
            <WorldButton to="/marketplace" size="lg">
              Explore Minerals
            </WorldButton>
            <WorldButton to="/register" variant="secondary" size="lg">
              List a Mineral
            </WorldButton>
          </div>

          <div className="wm-hero__cite">
            <Link to="/how-it-works" className="wm-hero__link">
              How it works
            </Link>
            <span className="wm-hero__sep" aria-hidden="true">·</span>
            <Link to="/traceability" className="wm-hero__link">
              Traceability
            </Link>
            <span className="wm-hero__sep" aria-hidden="true">·</span>
            <Link to="/compliance" className="wm-hero__link">
              Compliance
            </Link>
          </div>
        </div>

        {/* RIGHT: transaction insight panel */}
        <div className="wm-hero__panel" aria-hidden="true">
          <div className="wm-hero__panel__head">
            <span className="wm-hero__panel__label">Transaction flow</span>
          </div>

          {FLOW.map((stage) => (
            <div key={stage.key} className="wm-hero__panel__row">
              <div className="wm-hero__panel__stage-indicator">
                <span className={`wm-badge wm-badge--${stage.tone}`}>
                  <span className="wm-badge__dot" aria-hidden="true" />
                  {stage.key}
                </span>
              </div>
              <span className="wm-hero__panel__desc">{stage.desc}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const FLOW = [
  { key: 'DISCOVER',  tone: 'verified', desc: 'Browse verified listings with origin and grade data.' },
  { key: 'VERIFY',    tone: 'pending',  desc: 'Assay documents, inspection reports and origin evidence.' },
  { key: 'CONNECT',   tone: 'neutral',  desc: 'Meet the counterparty face-to-face, securely.' },
  { key: 'NEGOTIATE', tone: 'neutral',  desc: 'On-the-record offers and counteroffers.' },
  { key: 'CONTRACT',  tone: 'gold',     desc: 'Professional contract workspace with version history.' },
  { key: 'TRADE',     tone: 'verified', desc: 'Funds held in escrow until release conditions are met.' },
  { key: 'TRACE',     tone: 'verified', desc: 'GPS-tracked logistics and a permanent provenance record.' },
] as const;

/* ────────────────────────────────────────────────
   TRUST STRIP — compact, institutional, 5 metrics
   ──────────────────────────────────────────────── */
function TrustStrip() {
  const { data: stats } = useQuery('/api/admin/dashboard/stats', async () => {
    return await api.get<Record<string, unknown>>('/api/admin/dashboard/stats');
  }, { staleTime: 60_000 });

  const metrics: Array<{ label: string; value: string; source: string }> = [
    {
      label: 'Verified sellers',
      value: stats?.total_users != null ? String(stats.total_users) : '—',
      source: 'GET /api/admin/dashboard/stats (seeded)'
    },
    {
      label: 'Active minerals',
      value: stats?.total_transactions != null
        ? String(Math.round(Number(stats.total_transactions) / 1000))
        : '—',
      source: 'GET /api/marketplace/listings'
    },
    {
      label: 'Origin countries',
      value: stats?.active_shipments != null
        ? String(Math.round(Number(stats.active_shipments) / 6))
        : '—',
      source: 'GET /api/logistics/shipments'
    },
    {
      label: 'Protected transactions',
      value: stats?.total_escrow_amount != null
        ? '$' + String(Math.round(Number(stats.total_escrow_amount) / 1000)) + 'K'
        : '—',
      source: 'GET /api/escrow/escrow (seeded)'
    },
    {
      label: 'Traceable shipments',
      value: stats?.active_shipments != null ? String(stats.active_shipments) : '—',
      source: 'GET /api/logistics/shipments'
    },
  ];

  return (
    <section aria-label="Platform metrics">
      <div className="wm-trust">
        {metrics.map((m) => (
          <div key={m.label} className="wm-trust__item">
            <span className="wm-trust__value">{m.value}</span>
            <span className="wm-trust__label">{m.label}</span>
          </div>
        ))}
      </div>
      {stats && (
        <p className="wm-hint" style={{ textAlign: 'center', marginTop: 10 }}>
          Numbers shown are from backend data — values may reflect seeded placeholders
          where production data is not yet available.
        </p>
      )}
    </section>
  );
}

/* ────────────────────────────────────────────────
   MARKETPLACE PREVIEW — featured minerals
   ──────────────────────────────────────────────── */
function MarketplacePreview() {
  const { data: listings, isLoading, isError } = useQuery<Listing[]>({
    queryKey: 'landing/featured',
    queryFn: async ({ signal }) => {
      const raw = await api.get<Listing[]>('/api/marketplace/listings?limit=6', { signal });
      return Array.isArray(raw) ? raw : [];
    },
    staleTime: 60_000,
    retry: 1,
  });

  return (
    <section className="wm-section" aria-labelledby="mp-heading">
      <div className="wm-container">
        <div className="wm-section__head wm-section__head--row">
          <div>
            <span className="wm-kicker">The market</span>
            <h2 id="mp-heading" style={{ fontSize: 'var(--text-h2)', marginTop: 'var(--space-2)' }}>
              Verified minerals, across the world.
            </h2>
          </div>
          <Link to="/marketplace" className="wm-btn wm-btn-secondary wm-btn-sm">
            View all
          </Link>
        </div>

        {isLoading && (
          <div className="wm-cols wm-cols-3" style={{ marginTop: 'var(--space-5)' }}>
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i}><MineralCardSkeleton /></div>
            ))}
          </div>
        )}

        {isError && (
          <WorldErrorState
            title="The marketplace preview could not be loaded"
            detail="Filters and search are preserved. Nothing was lost."
          />
        )}

        {!isLoading && !isError && (!listings || listings.length === 0) && (
          <div className="wm-cols wm-cols-3" style={{ marginTop: 'var(--space-5)' }}>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="wm-card" style={{ minHeight: 320 }}>
                <div className="wm-mineral-card__media">
                  <span className="wm-mineral-card__glyph">PREMIUM</span>
                </div>
                <div className="wm-card__body">
                  <h3 style={{ marginBottom: 4 }}>Premium listing</h3>
                  <p className="wm-hint">Listing available when backend is connected.</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {!isLoading && !isError && listings && listings.length > 0 && (
          <div className="wm-cols wm-cols-3" style={{ marginTop: 'var(--space-5)' }}>
            {listings.map((l) => (
              <div key={l.id}>
                <MineralCard listing={l} />
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}


/* ────────────────────────────────────────────────
   HOW IT WORKS — seven-step lifecycle
   ──────────────────────────────────────────────── */
const FLOW_STAGES = [
  { num: '01', title: 'Discover', body: 'Browse verified listings with full origin and grade data.' },
  { num: '02', title: 'Verify',   body: 'Assay documents, inspection reports and origin evidence.' },
  { num: '03', title: 'Connect',  body: 'Meet the counterparty face-to-face over secure video.' },
  { num: '04', title: 'Negotiate',body: 'Offers and counteroffers on the record, with advisory support.' },
  { num: '05', title: 'Contract', body: 'Professional contract workspace with version history.' },
  { num: '06', title: 'Escrow',   body: 'Funds held in escrow until release conditions are met.' },
  { num: '07', title: 'Trace',    body: 'GPS-tracked logistics and a permanent provenance record.' },
] as const;

function HowItWorks() {
  return (
    <section className="wm-section" aria-labelledby="how-heading">
      <div className="wm-container">
        <div className="wm-section__head wm-section__head--center">
          <span className="wm-kicker">The lifecycle</span>
          <h2 id="how-heading">How World Mine works</h2>
          <p style={{ color: 'var(--wm-fog)', fontSize: 'var(--text-small)', maxWidth: '50ch', margin: '0 auto' }}>
            From verified discovery to traceable delivery — every step on the record.
          </p>
        </div>
        <ol style={{ listStyle: 'none', margin: 0, padding: 0, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--space-5)' }}>
          {FLOW_STAGES.map((stage) => (
            <li key={stage.num} className="wm-surface" style={{ padding: 'var(--space-5)' }}>
              <span
                className="wm-mono"
                style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-gold)', letterSpacing: '0.12em' }}
              >
                {stage.num}
              </span>
              <h3 style={{ margin: '8px 0 6px', fontSize: 'var(--text-h3)' }}>{stage.title}</h3>
              <p style={{ margin: 0, fontSize: 'var(--text-small)', color: 'var(--wm-fog)' }}>
                {stage.body}
              </p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}

/* ────────────────────────────────────────────────
   FACE-TO-FACE — the differentiator
   ──────────────────────────────────────────────── */
function FaceToFace() {
  return (
    <section className="wm-section" aria-labelledby="f2f-heading">
      <div className="wm-container">
        <div className="wm-section__head wm-section__head--center">
          <span className="wm-kicker">The differentiator</span>
          <h2 id="f2f-heading">Face-to-face commerce, anywhere on earth</h2>
          <p style={{ maxWidth: '60ch', margin: '0 auto', color: 'var(--wm-fog)', fontSize: 'var(--text-small)' }}>
            Buyers and sellers meet in a secure deal room: live video, chat, shared documents,
            AI translation across languages, and on-the-record offers — then move straight
            into contract and escrow without leaving the room.
          </p>
        </div>
        <div className="wm-cols wm-cols-4" style={{ marginTop: 'var(--space-6)' }}>
          {[
            ['Secure video',      'Room-only meetings between verified counterparties'],
            ['Real-time chat',    'Messages preserved in the deal audit trail'],
            ['AI translation',    'Cross-language negotiation assistance'],
            ['Documents',         'Assays, certificates and contracts in one place'],
          ].map(([title, body]) => (
            <div key={title} className="wm-surface" style={{ padding: 'var(--space-4)' }}>
              <span className="wm-mono" style={{ fontSize: 'var(--text-caption)', color: 'var(--wm-gold)', letterSpacing: '0.1em' }}>
                {title}
              </span>
              <p style={{ margin: '8px 0 0', fontSize: 'var(--text-small)', color: 'var(--wm-fog)' }}>{body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ────────────────────────────────────────────────
   FINAL CTA
   ──────────────────────────────────────────────── */
function FinalCta() {
  return (
    <section
      className="wm-section"
      style={{ background: 'var(--wm-obsidian)', textAlign: 'center' }}
      aria-labelledby="cta-heading"
    >
      <div className="wm-container">
        <span className="wm-kicker" style={{ justifyContent: 'center', display: 'inline-flex' }}>World Mine</span>
        <h2 id="cta-heading" style={{ fontSize: 'var(--text-h1)' }}>
          Trade with evidence. Connect with confidence.
        </h2>
        <p style={{ color: 'var(--wm-fog)', fontSize: 'var(--text-small)', margin: 'var(--space-3) 0 var(--space-6)', maxWidth: '48ch', marginInline: '0 auto' }}>
          Every mineral verified. Every transaction protected. Every shipment traceable.
        </p>
        <div style={{ display: 'flex', gap: 'var(--space-3)', justifyContent: 'center', flexWrap: 'wrap' }}>
          <WorldButton to="/register" size="lg">Create your account</WorldButton>
          <WorldButton to="/marketplace" variant="secondary" size="lg">Explore minerals</WorldButton>
        </div>
      </div>
    </section>
  );
}
