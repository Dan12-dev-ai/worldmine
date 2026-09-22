/**
 * World Mine — session context.
 * Derives role-aware navigation from the server-authoritative /api/auth/me.
 * Frontend never *decides* authorization — it only adapts navigation (§37).
 */
import React, { createContext, useContext, useMemo } from 'react';
import { useQuery } from 'react-query';
import { api, ApiError } from '../../shared/api/client';
import type { SessionUser } from '../../shared/types/domain';

interface SessionContextValue {
  user: SessionUser | null;
  isLoading: boolean;
  isAdmin: boolean;
  isAuthenticated: boolean;
  refetch: () => void;
}

const SessionContext = createContext<SessionContextValue>({
  user: null, isLoading: true, isAdmin: false, isAuthenticated: false, refetch: () => {},
});

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const { data, isLoading, refetch } = useQuery<SessionUser | null>(
    'auth/me',
    async () => {
      try {
        return await api.get<SessionUser>('/api/auth/me');
      } catch (err: unknown) {
        if (err instanceof ApiError && (err.status === 401 || err.status === 403)) return null;
        throw err;
      }
    },
    { staleTime: 60_000, retry: false, refetchOnWindowFocus: false },
  );

  const value = useMemo<SessionContextValue>(() => ({
    user: data ?? null,
    isLoading,
    // Fails closed: /api/auth/me sends no role today, so admin is false unless
    // the server actually asserts `user_type: "admin"`.
    isAdmin: data?.user_type === 'admin',
    isAuthenticated: Boolean(data),
    refetch: () => { void refetch(); },
  }), [data, isLoading, refetch]);


  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession() {
  return useContext(SessionContext);
}
