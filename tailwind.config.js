/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./frontend/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyber-navy': '#0a0e1a',
        'cyber-dark': '#050711',
        'neon-cyan': '#00ffff',
        'neon-emerald': '#10b981',
        'neon-gold': '#fbbf24',
        'glass-white': 'rgba(255, 255, 255, 0.05)',
        'glass-border': 'rgba(255, 255, 255, 0.1)',
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'float': 'float 3s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'particle': 'particle 20s linear infinite',
      },
      keyframes: {
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(0, 255, 255, 0.5)' },
          '100%': { boxShadow: '0 0 30px rgba(0, 255, 255, 0.8)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        particle: {
          '0%': { transform: 'translateX(-100px) translateY(0px)' },
          '100%': { transform: 'translateX(calc(100vw + 100px)) translateY(-100px)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
