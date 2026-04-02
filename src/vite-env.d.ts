/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_SUPABASE_URL: string;
  readonly VITE_SUPABASE_ANON_KEY: string;
  readonly VITE_ADMIN_USER_ID: string;
  readonly VITE_AUTH_SECRET: string;
  readonly SUPABASE_SERVICE_ROLE_KEY: string;
  readonly VITE_OPENAI_API_KEY: string;
  readonly VITE_STRIPE_PUBLISHABLE_KEY: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
