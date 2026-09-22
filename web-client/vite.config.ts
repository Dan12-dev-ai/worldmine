import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import { compression } from 'vite-plugin-compression2'
import path from 'path'

export default defineConfig(({ mode }) => {
  // Vite does not polyfill `process.env`, but this codebase (and
  // web-client/.env.example) uses CRA-style REACT_APP_* variables. Expose the
  // loaded vars through `process.env` so the existing code keeps working.
  const env = loadEnv(mode, process.cwd(), '')
  const appEnv = Object.fromEntries(
    Object.entries(env).filter(
      ([key]) => key.startsWith('VITE_') || key.startsWith('REACT_APP_')
    )
  )

  return {
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'masked-icon.svg'],
      manifest: {
        name: 'Worldmine - Global Marketplace',
        short_name: 'Worldmine',
        description: 'Global multi-language marketplace with AI-driven secure contracting and market news',
        theme_color: '#00d4ff',
        background_color: '#0a0e27',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    }),
    compression({
      algorithm: 'gzip',
      ext: '.gz'
    })
  ],
  root: '.',
  base: '/',
  publicDir: 'public',
  // Allow REACT_APP_* to be read via import.meta.env as well as process.env
  envPrefix: ['VITE_', 'REACT_APP_'],
  define: {
    'process.env': JSON.stringify({ NODE_ENV: mode, ...appEnv }),
  },
  // NOTE: the old `esbuild.loader: 'jsx'` override existed only for the legacy
  // src/index.js entry (JSX inside .js). main.tsx is now the entry and all
  // legacy screens are .jsx (natively handled by Vite + @vitejs/plugin-react).

  // Public review tunnels (pinggy / cloudflared / localtunnel) — the hostname
  // is dynamic per session, so allow the tunnel domains as subdomain wildcards.
  preview: {
    port: 4173,
    strictPort: true,
    allowedHosts: true,
    // The review build is served on the same origin as the API it calls: the
    // preview server proxies /api (and the websocket gateway) to the FastAPI app
    // so a tunnelled link exercises real endpoints instead of showing transport
    // errors. Override the target with VITE_API_TARGET when the API lives elsewhere.
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },

  build: {
    outDir: 'dist',
    emptyOutDir: true,
    target: 'esnext',
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      // Standard HTML entry — index.html loads /src/main.tsx (TS successor of index.js)
      input: './index.html',
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          supabase: ['@supabase/supabase-js'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-select', '@radix-ui/react-slot', '@radix-ui/react-tabs'],
          charts: ['recharts'],
          utils: ['clsx', 'tailwind-merge', 'framer-motion']
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    assetsInlineLimit: 4096
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
  server: {
    port: 3000,
    host: true
  },
  optimizeDeps: {
    include: ['react', 'react-dom', '@supabase/supabase-js'],
    esbuildOptions: {
      // Dependency scanning also has to allow JSX in .js files.
      loader: {
        '.js': 'jsx',
      },
    },
  }
  }
})
