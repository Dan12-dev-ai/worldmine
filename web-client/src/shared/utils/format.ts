/**
 * World Mine — display formatters (presentation only).
 *
 * These never invent a value: an absent/null field renders an explicit absence
 * marker ("—") so the interface never implies information it does not have
 * (§38 "no fabricated data", §47 "honest failure"). Enum values straight from
 * the backend serializers are rendered with underscores replaced by spaces.
 */

export const ABSENT = '—';

const NUM = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 });
const INT = new Intl.NumberFormat('en-US');

export function money(value: number | null | undefined, currency = 'USD'): string {
  if (typeof value !== 'number' || Number.isNaN(value)) return ABSENT;
  return currency === 'USD' ? `$${NUM.format(value)}` : `${NUM.format(value)} ${currency}`;
}

export function quantity(value: number | null | undefined, unit = 'units'): string {
  if (typeof value !== 'number' || Number.isNaN(value)) return ABSENT;
  return `${NUM.format(value)} ${unit}`;
}

export function percent(value: number | null | undefined): string {
  if (typeof value !== 'number' || Number.isNaN(value)) return ABSENT;
  return `${NUM.format(value)}%`;
}

export function count(value: number | null | undefined): string {
  if (typeof value !== 'number' || Number.isNaN(value)) return ABSENT;
  return INT.format(value);
}

export function date(value: string | null | undefined): string {
  if (!value) return ABSENT;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? ABSENT : d.toLocaleDateString();
}

export function dateTime(value: string | null | undefined): string {
  if (!value) return ABSENT;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? ABSENT : d.toLocaleString();
}

export function text(value: string | null | undefined): string {
  return value == null || value === '' ? ABSENT : value;
}

/** Backend enum value -> readable label (keeps the value verifiable). */
export function label(value: string | null | undefined): string {
  return value == null || value === '' ? ABSENT : value.replace(/_/g, ' ');
}

export function shortId(value: string | null | undefined, length = 8): string {
  if (!value) return ABSENT;
  return value.length > length ? `${value.slice(0, length)}…` : value;
}

export function duration(seconds: number | null | undefined): string {
  if (typeof seconds !== 'number' || Number.isNaN(seconds)) return ABSENT;
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

/**
 * Logistics serializes origin/destination as `Union[Dict[str, Any], str]`.
 * Render the structured form when the known keys exist, otherwise state plainly
 * that a structured record is on file rather than printing a raw object dump.
 */
export function address(value: unknown): string {
  if (value == null || value === '') return ABSENT;
  if (typeof value === 'string') return value;
  if (typeof value === 'object') {
    const o = value as Record<string, unknown>;
    const parts = [
      'line1', 'address_line1', 'street', 'city', 'state', 'postal_code', 'country',
    ]
      .map((k) => (typeof o[k] === 'string' ? (o[k] as string) : null))
      .filter((p): p is string => !!p && p.length > 0);
    return parts.length ? parts.join(', ') : 'Structured address on record';
  }
  return ABSENT;
}

/** Weight may arrive as `weight` or `weight_kg` (logistics serializer). */
export function weight(shipment: { weight?: number | null; weight_kg?: number | null }): string {
  const kg = shipment.weight_kg ?? shipment.weight;
  return typeof kg === 'number' ? `${NUM.format(kg)} kg` : ABSENT;
}

export const DATE_FIELDS = ['created_at', 'updated_at', 'published_at', 'timestamp'] as const;
