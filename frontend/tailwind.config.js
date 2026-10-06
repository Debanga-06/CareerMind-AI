/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0B1220',
        paper: '#F7F8FA',
        surface: '#FFFFFF',
        signal: {
          50: '#E6FBF3',
          100: '#C2F5E1',
          300: '#5DDBAE',
          500: '#00B37E',
          600: '#009468',
          700: '#00744F',
        },
        amber: {
          50: '#FEF6E7',
          100: '#FCE8C0',
          300: '#F7C568',
          500: '#F5A524',
          600: '#D3860F',
        },
        rose: {
          50: '#FDECED',
          100: '#FAD1D3',
          300: '#F08E92',
          500: '#E5484D',
          600: '#C43137',
        },
        line: '#E4E7EC',
        muted: '#5B6472',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        card: '0 1px 2px rgba(11, 18, 32, 0.04), 0 1px 1px rgba(11, 18, 32, 0.03)',
      },
      borderRadius: {
        xl2: '1.25rem',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: 0, transform: 'translateY(8px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        'draw-line': {
          '0%': { strokeDashoffset: 1000 },
          '100%': { strokeDashoffset: 0 },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.5s ease-out both',
        'draw-line': 'draw-line 1.8s ease-out forwards',
      },
    },
  },
  plugins: [],
}
