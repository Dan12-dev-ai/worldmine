/**
 * World Mine — public content pages.
 *
 * These replace the "under reconstruction" placeholders with real, reviewable
 * content: what each surface commits to and — where a capability is not wired
 * yet — which backend endpoint it depends on. Nothing here asserts a capability
 * the codebase cannot demonstrate (§38).
 */
import type { ReactNode } from 'react';
import { WorldButton, WorldBadge, LifecycleStepper } from '../../design-system';

function Page({ kicker, title, intro, children, actions }: {
  kicker: string;
  title: string;
  intro: string;
  children: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className="wm-container" style={{ padding: 'var(--space-8) var(--gutter)' }}>
      <div className="wm-section__head">
        <span className="wm-kicker">{kicker}</span>
        <h1 style={{ fontSize: 'var(--text-h1)', margin: '10px 0 8px' }}>{title}</h1>
        <p style={{ color: 'var(--wm-fog)', margin: 0 }}>{intro}</p>
      </div>
      {actions && (
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 'var(--space-6)' }}>{actions}</div>
      )}
      <div style={{ display: 'grid', gap: 'var(--space-5)' }}>{children}</div>
    </div>
  );
}

function Card({ title, children, tone }: { title: string; children: ReactNode; tone?: 'live' | 'pending' }) {
  return (
    <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
      <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
        <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>{title}</h2>
        {tone === 'live' && <WorldBadge tone="verified"><span className="wm-badge__dot" />live</WorldBadge>}
        {tone === 'pending' && <WorldBadge tone="pending"><span className="wm-badge__dot" />in progress</WorldBadge>}
      </div>
      <div style={{ marginTop: 12, color: 'var(--wm-fog)', display: 'grid', gap: 10 }}>{children}</div>
    </section>
  );
}

export function HowItWorksPage() {
  return (
    <Page
      kicker="How it works"
      title="One transaction spine, eleven stages"
      intro="Every deal on World Mine moves through the same lifecycle. Each stage names the party responsible, the action required and the evidence recorded — so a buyer, a seller and an auditor see the same truth."
      actions={<WorldButton to="/marketplace" variant="primary">Browse the marketplace</WorldButton>}
    >
      <section className="wm-surface" style={{ padding: 'var(--space-6)' }}>
        <LifecycleStepper />
      </section>

      <Card title="Discover & verify" tone="live">
        <p style={{ margin: 0 }}>
          Sellers publish listings with mineral type, quantity, grade, origin and price. Buyers search by mineral,
          country, grade and availability. Verification state is shown per listing when the backend supplies it,
          and reads “no verification submitted” when it does not — a listing is never implied to be verified
          without evidence.
        </p>
        <p className="wm-hint" style={{ margin: 0 }}>
          Endpoints: GET /api/marketplace/listings, GET /api/marketplace/listings/{'{id}'}
        </p>
      </Card>

      <Card title="Negotiate & contract" tone="live">
        <p style={{ margin: 0 }}>
          Agreed terms become a contract from a reusable template. Contracts record the parties, the stored
          content, the signature set and an append-only audit trail, and move through draft → pending signature →
          signed → active.
        </p>
        <p className="wm-hint" style={{ margin: 0 }}>
          Endpoints: GET /api/contracts/contracts, GET /api/contracts/templates
        </p>
      </Card>

      <Card title="Escrow, ship, complete" tone="live">
        <p style={{ margin: 0 }}>
          Funds are held against explicit release conditions. Shipment adds transport mode, route, weight and
          delivery state with a tracking lookup. The escrow register shows the current state, the next
          responsible party and the action required before money can move.
        </p>
        <p className="wm-hint" style={{ margin: 0 }}>
          Endpoints: GET /api/escrow/escrow, GET /api/logistics/shipments, GET /api/logistics/track/{'{number}'}
        </p>
      </Card>
    </Page>
  );
}
export function TraceabilityPage() {
  return (
    <Page
      kicker="Traceability"
      title="Evidence, not claims"
      intro="Traceability only means something when each step carries evidence a third party can check. World Mine stores the chain of custody alongside the deal rather than asking anyone to trust a summary."
    >
      <Card title="What is recorded today" tone="live">
        <ul style={{ margin: 0, paddingLeft: '1.15em', display: 'grid', gap: 8 }}>
          <li>Listing provenance fields: mineral type, grade, origin, country, city and coordinates where supplied.</li>
          <li>Contract audit trail: every state change with actor and timestamp.</li>
          <li>Shipment movement history: status, description, timestamp and GPS coordinates per event.</li>
          <li>Escrow milestones: which release condition was satisfied, and when.</li>
          <li>Administrative actions: a separate, append-only audit log.</li>
        </ul>
      </Card>

      <Card title="What must be added before this is a full chain of custody" tone="pending">
        <ul style={{ margin: 0, paddingLeft: '1.15em', display: 'grid', gap: 8 }}>
          <li>Assay and laboratory documents attached to a listing — the marketplace serializer does not embed verification evidence yet.</li>
          <li>Signed handover artefacts at warehouse and port gates.</li>
          <li>Independent third-party verification records with expiry dates.</li>
          <li>Export documentation (permits, certificate of origin) linked to the shipment.</li>
        </ul>
        <p className="wm-hint" style={{ margin: 0 }}>
          Until these exist this page states them as gaps rather than displaying a decorative “traceable” badge.
        </p>
      </Card>

      <Card title="Recorded stage sequence">
        <p className="wm-mono" style={{ margin: 0 }}>
          DISCOVER → VERIFY → CONNECT → NEGOTIATE → CONTRACT → ESCROW → PAY → SHIP → COMPLY → TRACE → COMPLETE
        </p>
      </Card>
    </Page>
  );
}



export function CompliancePage() {
  return (
    <Page
      kicker="Compliance"
      title="Controls stated plainly"
      intro="Compliance is a set of specific, testable controls — not a page of logos. Below is what the platform enforces today and what remains unimplemented."
    >
      <Card title="Enforced today" tone="live">
        <ul style={{ margin: 0, paddingLeft: '1.15em', display: 'grid', gap: 8 }}>
          <li>Server-authoritative authorisation: the frontend adapts navigation but never decides access.</li>
          <li>Route protection that fails closed — unauthenticated users are redirected to sign-in with a return path.</li>
          <li>Role-gated operator surfaces that deny access unless the server asserts the role claim.</li>
          <li>No financial mutation is ever fired implicitly or auto-retried by the client.</li>
          <li>Full audit trails for contracts, escrow milestones and administrative actions.</li>
        </ul>
      </Card>

      <Card title="Not yet implemented" tone="pending">
        <ul style={{ margin: 0, paddingLeft: '1.15em', display: 'grid', gap: 8 }}>
          <li>Sanctions and PEP screening against a maintained list.</li>
          <li>Automated export-permit validation per jurisdiction.</li>
          <li>Retention and erasure workflows with tenant-level evidence.</li>
          <li>Regional data-residency routing.</li>
        </ul>
        <p className="wm-hint" style={{ margin: 0 }}>
          Identity verification (KYC) endpoints exist, but that router depends on computer-vision packages that are
          not installed in this environment, so it is not mounted. That is reported here rather than hidden.
        </p>
      </Card>
    </Page>
  );
}

export function EsgPage() {
  return (
    <Page
      kicker="ESG"
      title="Measured, or marked unknown"
      intro="Environmental and social reporting is only credible when each figure has a stated origin. Where the platform has no measurement, it says so instead of publishing an estimate."
    >
      <Card title="Data the platform holds" tone="live">
        <ul style={{ margin: 0, paddingLeft: '1.15em', display: 'grid', gap: 8 }}>
          <li>Origin geography per listing (country, city, coordinates where provided).</li>
          <li>Transport mode per shipment — the basis for calculating freight emissions.</li>
          <li>Weight per shipment, so emissions factors can be applied to real tonnage.</li>
          <li>Site- and party-level verification state.</li>
        </ul>
      </Card>

      <Card title="Required before an ESG score can be published" tone="pending">
        <ul style={{ margin: 0, paddingLeft: '1.15em', display: 'grid', gap: 8 }}>
          <li>Audited emissions factors per transport mode and route.</li>
          <li>Mine-site environmental certification with validity periods.</li>
          <li>Social and labour compliance attestations per operator.</li>
          <li>A documented calculation methodology with a named owner.</li>
        </ul>
        <p className="wm-hint" style={{ margin: 0 }}>
          A numeric ESG score is deliberately not shown anywhere in this interface until those inputs exist.
        </p>
      </Card>
    </Page>
  );
}


export function SupportPage() {
  return (
    <Page
      kicker="Support"
      title="Getting help"
      intro="Support routes through the same record-keeping as the transaction itself, so an issue is always tied to a deal, contract, escrow or shipment."
    >
      <Card title="Include these references" tone="live">
        <ul style={{ margin: 0, paddingLeft: '1.15em', display: 'grid', gap: 8 }}>
          <li>The listing or order reference shown on the relevant screen.</li>
          <li>The contract, escrow or tracking reference, if the issue concerns one.</li>
          <li>The exact time the problem occurred and what you expected to happen.</li>
        </ul>
        <p className="wm-hint" style={{ margin: 0 }}>
          References are stable identifiers, not labels — quoting one lets an operator locate the record directly.
        </p>
      </Card>

      <Card title="Status of your request" tone="pending">
        <p style={{ margin: 0 }}>
          A ticket-status surface is not built yet: there is no support-ticket endpoint in the API contract, so any
          form placed here would silently discard what was submitted. Until that endpoint exists this page does not
          offer one.
        </p>
      </Card>

      <Card title="Go to">
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <WorldButton to="/marketplace" variant="secondary" size="sm">Marketplace</WorldButton>
          <WorldButton to="/how-it-works" variant="ghost" size="sm">How it works</WorldButton>
          <WorldButton to="/traceability" variant="ghost" size="sm">Traceability</WorldButton>
          <WorldButton to="/compliance" variant="ghost" size="sm">Compliance</WorldButton>
        </div>
      </Card>
    </Page>
  );
}
