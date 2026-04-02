/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly NEXT_PUBLIC_APP_URL: string;
  readonly NEXT_PUBLIC_APP_NAME: string;
  readonly NEXT_PUBLIC_APP_VERSION: string;
  readonly NEXT_PUBLIC_ADMIN_USER_ID: string;
  readonly NEXT_PUBLIC_AUTH_SECRET: string;
  readonly NEXT_PUBLIC_SUPABASE_URL: string;
  readonly NEXT_PUBLIC_SUPABASE_ANON_KEY: string;
  readonly NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY: string;
  readonly NEXT_PUBLIC_OPENAI_API_KEY: string;
  readonly NEXT_PUBLIC_CACHE_MAX_AGE: string;
  readonly NEXT_PUBLIC_SW_VERSION: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
