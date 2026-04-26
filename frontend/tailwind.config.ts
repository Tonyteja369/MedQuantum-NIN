import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class', '[data-theme="dark"]'],
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'bg-primary': '#0a0e1a',
        'bg-secondary': '#0f1424',
        'bg-tertiary': '#141929',
        'bg-card': 'rgba(255,255,255,0.03)',
        'border-primary': 'rgba(255,255,255,0.08)',
        'border-secondary': 'rgba(255,255,255,0.05)',
        'text-primary': '#f0f4ff',
        'text-secondary': '#8892b0',
        'text-muted': '#4a5568',
        'accent-primary': '#00d4ff',
        'accent-secondary': '#7c3aed',
        'accent-danger': '#ff4d6d',
        'accent-warning': '#fbbf24',
        'accent-success': '#10b981',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        'jetbrains-mono': ['JetBrains Mono', 'monospace'],
      },
      borderRadius: {
        sm: '6px',
        md: '10px',
        lg: '16px',
        xl: '24px',
      },
      boxShadow: {
        sm: '0 2px 8px rgba(0,0,0,0.3)',
        md: '0 4px 16px rgba(0,0,0,0.4)',
        lg: '0 8px 32px rgba(0,0,0,0.5)',
        'glow-primary': '0 0 20px rgba(0,212,255,0.3)',
        'glow-secondary': '0 0 20px rgba(124,58,237,0.3)',
        'glow-danger': '0 0 20px rgba(255,77,109,0.3)',
        'glow-success': '0 0 20px rgba(16,185,129,0.3)',
      },
      animation: {
        'ecg-trace': 'ecg-trace 3s linear infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite alternate',
        'fade-up': 'fade-up 0.4s ease-out',
        'slide-in-right': 'slide-in-right 0.3s ease-out',
        shimmer: 'shimmer 2s linear infinite',
        heartbeat: 'heartbeat 1.4s ease-in-out infinite',
      },
      keyframes: {
        'ecg-trace': {
          '0%': { strokeDashoffset: '1000' },
          '100%': { strokeDashoffset: '0' },
        },
        'pulse-glow': {
          '0%': { boxShadow: 'none' },
          '100%': { boxShadow: '0 0 20px rgba(0,212,255,0.3)' },
        },
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          '0%': { opacity: '0', transform: 'translateX(16px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        heartbeat: {
          '0%, 100%': { transform: 'scale(1)' },
          '14%': { transform: 'scale(1.15)' },
          '28%': { transform: 'scale(1)' },
          '42%': { transform: 'scale(1.1)' },
          '56%': { transform: 'scale(1)' },
        },
      },
      backdropBlur: {
        xs: '4px',
      },
    },
  },
  plugins: [],
}

export default config
