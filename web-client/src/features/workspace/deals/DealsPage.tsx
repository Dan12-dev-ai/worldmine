/**
 * World Mine — Deal Rooms (/deals, Phase 6).
 *
 * Reads the trading surface: orders, recent trades, performance metrics.
 *
 * DOCUMENTED DRIFT (shown, not hidden — §48): `/api/trading/orders` and
 * `/api/trading/trades` are typed `List[Dict[str, Any]]` server-side and today
 * return seeded rows, and the trading routes authenticate with a placeholder
 * dependency rather than a verified JWT. This screen therefore presents exactly
 * what the API returns and never labels it "verified trading history".
 */
import { ModuleFrame } from '../ModuleFrame';
import { DataPanel, StatGrid } from '../DataPanel';
import type { Column } from '../DataPanel';
import { errorDetail, useResource, useResourceList } from '../useResource';
import type { Trade, TradingOrder, TradingPerformance } from '../../../shared/types/domain';
import { ABSENT, count, dateTime, label, money, percent, quantity, shortId } from '../../../shared/utils/format';
import { WorldButton, WorldStatus } from '../../../design-system';

const ORDER_COLUMNS: Column<TradingOrder>[] = [
  {
    key: 'order',
    header: 'Order',
    nowrap: true,
    render: (o) => <span className="wm-mono">{shortId(o.order_id ?? o.id ?? null)}</span>,
  },
  { key: 'mineral', header: 'Mineral', render: (o) => label(o.mineral_id) },
  { key: 'side', header: 'Side', render: (o) => label(o.side) },
  { key: 'type', header: 'Type', render: (o) => label(o.order_type) },
  { key: 'qty', header: 'Quantity', align: 'right', render: (o) => quantity(o.quantity) },
  { key: 'price', header: 'Price', align: 'right', render: (o) => money(o.price) },
  { key: 'filled', header: 'Filled', align: 'right', render: (o) => quantity(o.filled_quantity) },
  { key: 'status', header: 'Status', render: (o) => (o.status ? <WorldStatus status={o.status} /> : ABSENT) },
  { key: 'created', header: 'Created', nowrap: true, render: (o) => dateTime(o.created_at) },
];

const TRADE_COLUMNS: Column<Trade>[] = [
  {
    key: 'trade',
    header: 'Trade',
    nowrap: true,
    render: (t) => <span className="wm-mono">{shortId(t.trade_id ?? null)}</span>,
  },
  { key: 'mineral', header: 'Mineral', render: (t) => label(t.mineral_id) },
  { key: 'side', header: 'Side', render: (t) => label(t.side) },
  { key: 'amount', header: 'Amount', align: 'right', render: (t) => quantity(t.amount) },
  { key: 'price', header: 'Price', align: 'right', render: (t) => money(t.price) },
  {
    key: 'total',
    header: 'Total',
    align: 'right',
    render: (t) =>
      money(
        t.total ??
          (typeof t.amount === 'number' && typeof t.price === 'number' ? t.amount * t.price : null),
      ),
  },
  { key: 'status', header: 'Status', render: (t) => (t.status ? <WorldStatus status={t.status} /> : ABSENT) },
  { key: 'executed', header: 'Executed', nowrap: true, render: (t) => dateTime(t.executed_at ?? null) },
];

export function DealsPage() {
  const orders = useResourceList<TradingOrder>('/api/trading/orders?limit=50');
  const trades = useResourceList<Trade>('/api/trading/trades?limit=25');
  const performance = useResource<TradingPerformance>('/api/trading/performance');

  return (
    <ModuleFrame
      title="Deal Rooms"
      blurb="Orders, executed trades and performance for your account. Negotiation rooms with video, documents and AI assistance follow in the next phase."
      sources={['GET /api/trading/orders', 'GET /api/trading/trades', 'GET /api/trading/performance']}
      actions={
        <>
          <WorldButton to="/marketplace" variant="secondary">Find minerals</WorldButton>
          <WorldButton to="/contracts" variant="ghost">Contracts</WorldButton>
        </>
      }
    >
      {performance.data ? (
        <StatGrid
          title="Performance"
          items={[
            { label: 'Trades', value: count(performance.data.total_trades) },
            { label: 'Volume', value: money(performance.data.total_volume), tone: 'gold' },
            {
              label: 'P&L',
              value: money(performance.data.total_pnl),
              tone: (performance.data.total_pnl ?? 0) < 0 ? 'warning' : 'verified',
            },
            { label: 'Win rate', value: percent(performance.data.win_rate) },
          ]}
        />
      ) : (
        <section className="wm-surface" style={{ padding: 'var(--space-5)' }}>
          <h2 style={{ fontSize: 'var(--text-h3)', margin: 0 }}>Performance</h2>
          <p className="wm-hint" style={{ margin: '6px 0 0', maxWidth: '70ch' }}>
            {performance.isLoading
              ? 'Loading performance metrics…'
              : 'Performance metrics are unavailable right now ('
                + `${performance.isError ? errorDetail(performance.error) : 'endpoint returned no data'}). `
                + 'Nothing is estimated in its place.'}
          </p>
          {performance.isError && (
            <button
              type="button"
              className="wm-btn wm-btn-secondary wm-btn-sm"
              style={{ marginTop: 12 }}
              onClick={performance.refetch}
            >
              Retry
            </button>
          )}
        </section>
      )}

      <DataPanel
        title="Open orders"
        description="Every order returned for the authenticated trading identity."
        rows={orders.rows}
        columns={ORDER_COLUMNS}
        rowKey={(o, i) => o.order_id ?? o.id ?? `order-${i}`}
        isLoading={orders.isLoading}
        isError={orders.isError}
        errorDetail={errorDetail(orders.error)}
        onRetry={orders.refetch}
        emptyTitle="No orders yet"
        emptyHint="When you place an order on a mineral it appears here with its fill state."
        limitedTo={25}
      />

      <DataPanel
        title="Recent trades"
        description="Executed trades reported by the trading engine."
        rows={trades.rows}
        columns={TRADE_COLUMNS}
        rowKey={(t, i) => t.trade_id ?? `trade-${i}`}
        isLoading={trades.isLoading}
        isError={trades.isError}
        errorDetail={errorDetail(trades.error)}
        onRetry={trades.refetch}
        emptyTitle="No executed trades"
        emptyHint="Trades appear here once an order is matched and settled."
        limitedTo={15}
      />
    </ModuleFrame>
  );
}
