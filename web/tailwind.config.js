/**** @type {import('tailwindcss').Config} ****/
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f5f7ff',
          100: '#e9edff',
          200: '#cdd6ff',
          300: '#a9b6ff',
          400: '#7b8dff',
          500: '#4e64ff',
          600: '#2b45f3',
          700: '#1f35c2',
          800: '#1b2e9a',
          900: '#172875',
        },
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: 0, transform: 'translateY(6px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 300ms ease-out both',
      },
      boxShadow: {
        'glow': '0 0 0 3px rgba(78,100,255,0.25)',
      },
    },
  },
  plugins: [],
};