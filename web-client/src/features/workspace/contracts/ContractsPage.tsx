/**
 * World Mine — Contracts (/contracts, Phase 7).
 *
 * Two real endpoints: the contract register and the reusable template library.
 * A selected contract shows its stored content, parties and signature count —
 * read-only here; signing/activation are mutations and stay out of this screen
 * until the signature flow is specified (§63: financial/legal actions are never
 * fired implicitly).
 */
import { useState } from 'react';
import { ModuleFrame } from '../ModuleFrame';
import { DataPanel } from '../DataPanel';
import type { Column } from '../DataPanel';
import { errorDetail, useResourceList } from '../useResource';
import type { Contract, ContractTemplate } from '../../../shared/types/domain';
import { ABSENT, count, dateTime, label, shortId, text } from '../../../shared/utils/format';
import { WorldBadge, WorldButton, WorldStatus } from '../../../design-system';

const CONTRACT_COLUMNS: Column<Contract>[] = [
  {
    key: 'id',
    header: 'Contract',
    nowrap: true,
    render: (c) => <span className="wm-mono">{shortId(c.id)}</span>,
  },
  { key: 'type', header: 'Type', render: (c) => label(c.contract_type) },
  { key: 'status', header: 'Status', render: (c) => (c.status ? <WorldStatus status={c.status} /> : ABSENT) },
  {
    key: 'parties',
    header: 'Parties',
    align: 'right',
    render: (c) => count(c.parties?.length ?? 0),
  },
  {
    key: 'signatures',
    header: 'Signatures',
    align: 'right',
    render: (c) => count(c.signatures?.length ?? 0),
  },
  { key: 'created', header: 'Created', nowrap: true, render: (c) => dateTime(c.created_at) },
];

const TEMPLATE_COLUMNS: Column<ContractTemplate>[] = [
  { key: 'name', header: 'Template', render: (t) => text(t.name) },
  { key: 'type', header: 'Type', render: (t) => label(t.contract_type) },
  {
    key: 'variables',
    header: 'Variables',
    align: 'right',
    render: (t) => count(t.variables?.length ?? 0),
  },
  { key: 'id', header: 'Reference', nowrap: true, render: (t) => <span className="wm-mono">{shortId(t.id)}</span> },
];

export function ContractsPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const contracts = useResourceList<Contract>('/api/contracts/contracts?limit=50');
  const templates = useResourceList<ContractTemplate>('/api/contracts/templates');

  const selected = contracts.rows?.find((c) => c.id === selectedId) ?? null;

  const columns: Column<Contract>[] = [
    ...CONTRACT_COLUMNS,
    {
      key: 'open',
      header: '',
      align: 'right',
      render: (c) => (
        <button
          type="button"
          className="wm-btn wm-btn-ghost wm-btn-sm"
          aria-pressed={c.id === selectedId}
          onClick={() => setSelectedId(c.id === selectedId ? null : c.id)}
        >
          {c.id === selectedId ? 'Close' : 'Inspect'}
        </button>
      ),
    },
  ];

  return (
    <ModuleFrame
      title="Contracts"
      blurb="Contract register and template library: parties, machine-readable terms, stored clauses and signature state."
      sources={['GET /api/contracts/contracts', 'GET /api/contracts/templates']}
      actions={<WorldButton to="/escrow" variant="secondary">Escrow</WorldButton>}
    >
      <DataPanel
        title="Contract register"
        description="Every contract on record. Inspection is read-only until the signature flow is specified."
        rows={contracts.rows}
        columns={columns}
        rowKey={(c) => c.id}
        isLoading={contracts.isLoading}
        isError={contracts.isError}
        errorDetail={errorDetail(contracts.error)}
        onRetry={contracts.refetch}
        emptyTitle="No contracts yet"
        emptyHint="Contracts raised from a marketplace deal appear here with their state and signatures."
        limitedTo={25}
      >
        {selected && (
          <div style={{ marginTop: 'var(--space-5)', borderTop: 'var(--border-hairline)', paddingTop: 'var(--space-5)' }}>
            <div style={{ display: 'flex', gap: 10, alignItems: 'center', flexWrap: 'wrap' }}>
              <h3 style={{ margin: 0, fontSize: 'var(--text-h3)' }}>{label(selected.contract_type)}</h3>
              <WorldBadge tone="neutral">{shortId(selected.id, 12)}</WorldBadge>
              {selected.status && <WorldStatus status={selected.status} />}
            </div>

            <dl className="wm-mono" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-4)', margin: 'var(--space-5) 0 0' }}>
              <div>
                <dt className="wm-label">Template</dt>
                <dd style={{ margin: 0 }}>{shortId(selected.template_id)}</dd>
              </div>
              <div>
                <dt className="wm-label">Created</dt>
                <dd style={{ margin: 0 }}>{dateTime(selected.created_at)}</dd>
              </div>
              <div>
                <dt className="wm-label">Audit entries</dt>
                <dd style={{ margin: 0 }}>{count(selected.audit_trail?.length ?? 0)}</dd>
              </div>
            </dl>

            <h4 style={{ margin: 'var(--space-5) 0 8px', fontSize: 'var(--text-body)' }}>Parties</h4>
            {selected.parties?.length ? (
              <ul style={{ margin: 0, paddingLeft: '1.1em', display: 'grid', gap: 6 }}>
                {selected.parties.map((p, i) => (
                  <li key={`${p.name ?? 'party'}-${i}`}>
                    {text(p.name ?? p.user_id)} — {label(p.role)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="wm-hint" style={{ margin: 0 }}>No parties recorded on this contract.</p>
            )}

            <h4 style={{ margin: 'var(--space-5) 0 8px', fontSize: 'var(--text-body)' }}>Stored content</h4>
            <pre
              className="wm-mono"
              style={{
                margin: 0, padding: 'var(--space-4)', background: 'var(--wm-obsidian)',
                border: 'var(--border-hairline)', borderRadius: 'var(--radius-md)',
                whiteSpace: 'pre-wrap', maxHeight: 320, overflow: 'auto', fontSize: 'var(--text-data)',
              }}
            >
              {selected.content ? selected.content : 'No content stored on this contract.'}
            </pre>
          </div>
        )}
      </DataPanel>

      <DataPanel
        title="Template library"
        description="Reusable contract templates and the variables each one expects."
        rows={templates.rows}
        columns={TEMPLATE_COLUMNS}
        rowKey={(t) => t.id}
        isLoading={templates.isLoading}
        isError={templates.isError}
        errorDetail={errorDetail(templates.error)}
        onRetry={templates.refetch}
        emptyTitle="No templates published"
        emptyHint="Templates are created by sellers and operations; once published they are reusable for new deals."
      />
    </ModuleFrame>
  );
}
