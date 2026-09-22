/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string;
  readonly REACT_APP_API_URL?: string;
  readonly VITE_WS_URL?: string;
  readonly REACT_APP_WS_URL?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}

/* Legacy untyped JSX modules consumed by the TS layer (Phase 10 migration).
   reportWebVitals / AnalyticsProvider are declared in colocated .d.ts files. */
declare module '*/locales/translations' {
  export const translations: Record<string, Record<string, unknown>> | undefined;
  export function detectLanguage(): string;
  export function getTranslation(key: string, language?: string): string;
}
