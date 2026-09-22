/**
 * World Mine — React Query hooks for the auth domain.
 * Thin wrappers over the /api/auth contract. Server-authoritative.
 */
import { useMutation, useQuery } from 'react-query';
import { api, ApiError } from '../../shared/api/client';
import type { User } from '../../shared/types/domain';

interface RegisterResponse {
  message: string;
  email_sent?: boolean;
  user_id?: string | null;
}

export function useRegister() {
  return useMutation<RegisterResponse, ApiError, { email: string; username?: string; user_type?: string }>(
    (payload) => api.post('/api/auth/register', payload),
  );
}

export function usePasswordLogin() {
  return useMutation<Record<string, unknown>, ApiError, { username_or_email: string; password: string }>(
    (payload) => api.post('/api/auth/login', payload),
  );
}

/** GET /api/auth/me — current user, null when unauthenticated. */
export function useCurrentUser() {
  return useQuery<User | null, ApiError>('auth/me', async () => {
    try {
      return await api.get<User>('/api/auth/me');
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) return null;
      throw err;
    }
  }, {
    staleTime: 60_000,
    retry: false,
  });
}

export function useLogout() {
  return useMutation<unknown, ApiError>(() => api.post('/api/auth/logout'));
}

/** Password strength — used at registration (POST /check-password-strength). */
export function usePasswordStrength() {
  return useMutation<{ strength: string; score?: number }, ApiError, { password: string }>(
    (payload) => api.post('/api/auth/check-password-strength', payload),
  );
}
