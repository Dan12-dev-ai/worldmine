/**
 * World Mine — realtime provider (Phase 1 infrastructure).
 * Wraps the EXISTING WebSocket contract: /api/ws/{user_id} (connection gateway)
 * and /api/trading/ws (trading). Do not duplicate — this is the single client.
 * Handles reconnect with backoff, reduced-motion-agnostic, no event fabrication.
 */
import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import type { RealtimeEvent } from '../../shared/types/domain';
import { WS_BASE } from '../../shared/api/client';

type EventHandler = (event: RealtimeEvent) => void;

interface RealtimeContextValue {
  status: 'connecting' | 'connected' | 'disconnected' | 'offline';
  subscribe: (handler: EventHandler) => () => void;
  /** send a raw payload over the gateway socket (no-op when not connected) */
  send: (payload: unknown) => void;
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null);

const MAX_BACKOFF_MS = 20_000;

export function RealtimeProvider({ children, userId }: { children: React.ReactNode; userId?: string | null }) {
  const [status, setStatus] = useState<RealtimeContextValue['status']>('disconnected');
  const handlersRef = useRef(new Set<EventHandler>());
  const socketRef = useRef<WebSocket | null>(null);
  const attemptRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const disposedRef = useRef(false);

  const subscribe = useCallback((handler: EventHandler) => {
    handlersRef.current.add(handler);
    return () => { handlersRef.current.delete(handler); };
  }, []);

  const send = useCallback((payload: unknown) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(payload));
    }
  }, []);

  useEffect(() => {
    disposedRef.current = false;

    const connect = () => {
      if (disposedRef.current) return;
      if (!userId || typeof WebSocket === 'undefined') {
        setStatus('offline');
        return;
      }
      setStatus('connecting');
      const url = `${WS_BASE || window.location.origin.replace(/^http/, 'ws')}/api/ws/${encodeURIComponent(userId)}`;
      let ws: WebSocket;
      try {
        ws = new WebSocket(url);
      } catch {
        scheduleReconnect();
        return;
      }
      socketRef.current = ws;

      ws.onopen = () => {
        attemptRef.current = 0;
        setStatus('connected');
      };
      ws.onmessage = (raw) => {
        try {
          const parsed = JSON.parse(typeof raw.data === 'string' ? raw.data : '');
          const event: RealtimeEvent = {
            id: String(parsed?.id ?? `${Date.now()}-${Math.random().toString(16).slice(2)}`),
            type: String(parsed?.type ?? 'unknown'),
            timestamp: String(parsed?.timestamp ?? new Date().toISOString()),
            entity: String(parsed?.entity ?? parsed?.room ?? ''),
            payload: parsed?.payload ?? parsed,
            version: Number(parsed?.version ?? 1),
          };
          handlersRef.current.forEach((h) => {
            try { h(event); } catch { /* one bad handler must not kill the rest */ }
          });
        } catch {
          /* malformed frame — ignore, never fabricate */
        }
      };
      ws.onclose = () => {
        socketRef.current = null;
        if (!disposedRef.current) scheduleReconnect();
      };
      ws.onerror = () => {
        try { ws.close(); } catch { /* noop */ }
      };
    };

    const scheduleReconnect = () => {
      if (disposedRef.current) return;
      setStatus('disconnected');
      const delay = Math.min(2 ** attemptRef.current * 1000, MAX_BACKOFF_MS);
      attemptRef.current += 1;
      timerRef.current = setTimeout(connect, delay);
    };

    // Pause reconnect churn when tab is hidden (battery + no WS storms, §51)
    const onVisibility = () => {
      if (document.visibilityState === 'visible' && !socketRef.current && userId) {
        attemptRef.current = 0;
        connect();
      }
    };
    document.addEventListener('visibilitychange', onVisibility);

    connect();
    return () => {
      disposedRef.current = true;
      document.removeEventListener('visibilitychange', onVisibility);
      if (timerRef.current) clearTimeout(timerRef.current);
      try { socketRef.current?.close(); } catch { /* noop */ }
      socketRef.current = null;
    };
  }, [userId]);

  const value = useMemo(
    () => ({ status, subscribe, send }),
    [status, subscribe, send],
  );

  return <RealtimeContext.Provider value={value}>{children}</RealtimeContext.Provider>;
}

export function useRealtime() {
  const ctx = useContext(RealtimeContext);
  if (!ctx) throw new Error('useRealtime must be used within RealtimeProvider');
  return ctx;
}

/** Subscribe to a specific event type with automatic cleanup. */
export function useRealtimeEvent(type: string | null, handler: EventHandler) {
  const { subscribe } = useRealtime();
  const handlerRef = useRef(handler);
  handlerRef.current = handler;
  useEffect(() => {
    if (!type) return;
    return subscribe((event) => {
      if (event.type === type) handlerRef.current(event);
    });
  }, [type, subscribe]);
}
