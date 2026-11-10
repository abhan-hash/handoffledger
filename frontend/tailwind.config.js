/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        canvas: '#d8daf0',
        canvasDark: '#090a12',
        surfaceLight: '#ffffff',
        surfaceDark: '#0c0e18',
        background: '#090a0f',
        surface: '#11131c',
        surfaceHover: '#181b27',
        borderSubtle: 'rgba(255, 255, 255, 0.08)',
        accent: '#3b82f6',
        accentHover: '#2563eb',
        accentGreen: '#10b981',
        accentPurple: '#8b5cf6',
        accentAmber: '#f59e0b',
        accentRose: '#f43f5e',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
      borderRadius: {
        '3xl': '24px',
        '4xl': '32px',
        '5xl': '40px',
      },
      boxShadow: {
        'subtle-glow': '0 0 20px -5px rgba(59, 130, 246, 0.15)',
        'floating-card': '0 12px 32px -4px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.04)',
        'tactile-card': '0 24px 48px -12px rgba(18, 20, 40, 0.12)',
        'glow-green': '0 0 30px -5px rgba(16, 185, 129, 0.35)',
        'glow-purple': '0 0 30px -5px rgba(139, 92, 246, 0.35)',
      }
    },
  },
  plugins: [],
}
