/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './main.tsx',
    './src/**/*.{js,jsx,ts,tsx}',
    // Shared component library consumed by this app
    '../frontend/src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Brand palette used by the Planetary / Spatial glass UI
        dedan: {
          bg: '#0a0e27',
          accent: '#00d4ff',
        },
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [],
};
