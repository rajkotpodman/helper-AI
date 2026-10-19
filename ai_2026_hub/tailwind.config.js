/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#080B11",
        surface: "rgba(15, 23, 42, 0.65)",
        "surface-border": "rgba(0, 242, 254, 0.2)",
        "bio-cyan": "#00F2FE",
        "pulse-teal": "#4FACFE",
        "energy-amber": "#FFB300",
        "alignment-red": "#FF2A6D",
        "text-primary": "#F8FAFC",
        "text-muted": "#94A3B8"
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace']
      },
      boxShadow: {
        'glow-cyan': '0 0 25px rgba(0, 242, 254, 0.35)',
        'glow-teal': '0 0 25px rgba(79, 172, 254, 0.35)',
        'glow-amber': '0 0 25px rgba(255, 179, 0, 0.35)',
        'glow-red': '0 0 25px rgba(255, 42, 109, 0.4)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)'
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'synapse': 'synapse 2s ease-in-out infinite'
      },
      keyframes: {
        glow: {
          '0%': { filter: 'drop-shadow(0 0 4px rgba(0, 242, 254, 0.4))' },
          '100%': { filter: 'drop-shadow(0 0 16px rgba(0, 242, 254, 0.8))' }
        }
      }
    },
  },
  plugins: [],
}
