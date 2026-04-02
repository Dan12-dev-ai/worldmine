/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  output: 'export',
  trailingSlash: true,
  images: {
    domains: ['localhost:3000', 'worldmine.vercel.app'],
    unoptimized: true
  },
  // PWA Configuration
  pwa: {
    dest: 'public',
    register: true,
    skipWaiting: true,
    runtimeCaching: [
      {
        urlPattern: /^https?.*\/api\/.*$/,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: {
            maxEntries: 50,
            maxAgeSeconds: 60 * 60 * 24 // 24 hours
          }
        }
      },
      {
        urlPattern: /^https?.*\/news\/.*$/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'news-cache',
          expiration: {
            maxEntries: 100,
            maxAgeSeconds: 60 * 60 * 24 * 7 // 7 days
          }
        }
      },
      {
        urlPattern: /\.(?:js|css|png|jpg|jpeg|svg|ico)$/,
        handler: 'CacheFirst',
        options: {
          cacheName: 'static-assets',
          expiration: {
            maxEntries: 200,
            maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
          }
        }
      }
    ]
  },
  // Performance optimizations for East Africa
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', 'framer-motion']
  },
  // Edge optimization
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()'
          }
        ]
      }
    ];
  }
}

module.exports = nextConfig
