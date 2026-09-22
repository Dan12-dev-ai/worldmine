/**
 * World Mine — typed API client (Phase 1).
 * Wraps the existing backend endpoints documented in
 * docs/FRONTEND_MIGRATION_MAP.md. Same URLs, typed + abortable.
 * Never silently fakes failed responses (§47, §38).
 */

const API_BASE = import.meta.env?.VITE_API_URL || import.meta.env?.REACT_APP_API_URL || '';
const WS_BASE = import.meta.env?.VITE_WS_URL || import.meta.env?.REACT_APP_WS_URL || '';

export { API_BASE, WS_BASE };

export class ApiError extends Error {
  constructor(public status: number, message: string, public detail?: unknown) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  signal?: AbortSignal;
  /** extra headers (auth tokens are added by the session layer, not here) */
  headers?: Record<string, string>;
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, signal, headers } = opts;
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    signal,
    headers: {
      ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
      ...headers,
    },
    credentials: 'include', // HttpOnly cookie sessions when backend supports them (§14)
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail: unknown = null;
    try { detail = await res.json(); } catch { /* non-JSON error body */ }
    const message =
      (detail as { detail?: { message?: string } | string } | null)?.detail != null
        ? typeof (detail as { detail: { message?: string } }).detail === 'string'
          ? (detail as { detail: string }).detail
          : ((detail as { detail: { message?: string } }).detail.message ?? `Request failed (${res.status})`)
        : `Request failed (${res.status})`;
    throw new ApiError(res.status, message, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/* Exponential backoff retry — read-only calls only (never retry financial POSTs, §63) */
export async function getWithRetry<T>(path: string, opts: RequestOptions = {}, retries = 2): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await request<T>(path, { ...opts, method: 'GET' });
    } catch (err) {
      lastError = err;
      if (err instanceof ApiError && err.status >= 400 && err.status < 500) throw err; // no retry on 4xx
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, 2 ** attempt * 400));
      }
    }
  }
  throw lastError;
}

export const api = {
  get: <T>(path: string, opts?: RequestOptions) => request<T>(path, { ...opts, method: 'GET' }),
  post: <T>(path: string, body?: unknown, opts?: RequestOptions) => request<T>(path, { ...opts, method: 'POST', body }),
  put: <T>(path: string, body?: unknown, opts?: RequestOptions) => request<T>(path, { ...opts, method: 'PUT', body }),
  delete: <T>(path: string, opts?: RequestOptions) => request<T>(path, { ...opts, method: 'DELETE' }),
};
