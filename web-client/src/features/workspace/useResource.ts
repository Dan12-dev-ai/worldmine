/**
 * World Mine — workspace data access (Phase 6–9).
 *
 * One hook used by every workspace module so they all behave identically and
 * contract-faithfully:
 *   - GET only through the typed API client; mutations are explicit elsewhere
 *     and are never retried (financial calls, §63).
 *   - Loading / error / empty are kept strictly separate — the module reports a
 *     failure rather than rendering an empty table that hides it (§47).
 *   - List payloads are normalised from BOTH shapes the backend actually uses:
 *     a bare JSON array (marketplace, contracts, logistics, notifications) and
 *     the `{"data": [...]}` envelope (escrow). An unrecognised shape returns
 *     `null` so the caller can surface a contract break instead of "no data".
 */
import { useQuery } from 'react-query';
import { api } from '../../shared/api/client';
import type { DataEnvelope } from '../../shared/types/domain';

export interface ResourceOptions {
  staleTime?: number;
  retry?: number;
  enabled?: boolean;
}

export interface ResourceResult<T> {
  data: T | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useResource<T>(path: string, options: ResourceOptions = {}): ResourceResult<T> {
  const { staleTime = 60_000, retry = 1, enabled = true } = options;

  const query = useQuery<T, Error>({
    queryKey: path,
    queryFn: async ({ signal }) => api.get<T>(path, { signal }),
    enabled,
    staleTime,
    retry,
  });

  return {
    data: query.data,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error ?? null,
    refetch: () => {
      void query.refetch();
    },
  };
}

/**
 * Normalises a list response. Returns `null` when the payload is neither an
 * array nor an array envelope — never an empty array, which would be a lie.
 */
export function asList<T>(payload: unknown): T[] | null {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === 'object') {
    const envelope = payload as DataEnvelope<unknown>;
    if (Array.isArray(envelope.data)) return envelope.data as T[];
  }
  return null;
}

/** Convenience wrapper: typed list + normalisation + honest shape check. */
export function useResourceList<T>(path: string, options: ResourceOptions = {}) {
  const resource = useResource<unknown>(path, options);
  return {
    rows: resource.isLoading || resource.isError ? null : asList<T>(resource.data),
    isLoading: resource.isLoading,
    isError: resource.isError,
    error: resource.error,
    refetch: resource.refetch,
  };
}

/** Human-readable error text for `WorldErrorState` (never swallowed). */
export function errorDetail(error: Error | null | undefined): string | undefined {
  if (!error) return undefined;
  return error.message || error.name;
}
