/**
 * World Mine — default react-query v3 queryFn (Phase 1).
 * Lets hooks pass a plain API path as the query key: useQuery('/api/marketplace').
 * Only GET; mutations go through the typed `api` client explicitly.
 */
import { api } from './client';

export function defaultQueryFn<T = unknown>({ queryKey }: { queryKey: unknown }): Promise<T> {
  const key = Array.isArray(queryKey) ? queryKey[0] : queryKey;
  if (typeof key !== 'string' || !key.startsWith('/')) {
    return Promise.reject(new Error(`defaultQueryFn: invalid query key ${JSON.stringify(queryKey)}`));
  }
  return api.get<T>(key);
}
