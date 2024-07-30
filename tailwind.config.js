// tailwind.config.js
module.exports = {
  darkMode: 'class', // ou 'media' pour le mode sombre automatique
  theme: {
    extend: {
      colors: {
        primary: {
          "50": "#eff6ff",
          "100": "#dbeafe",
          "200": "#bfdbfe",
          "300": "#93c5fd",
          "400": "#60a5fa",
          "500": "#3b82f6",
          "600": "#2563eb",
          "700": "#1d4ed8",
          "800": "#1e40af",
          "900": "#1e3a8a",
          "950": "#172554",
        },
        cyan: {
          100: '#E0F7FA',
          200: '#B2EBF2',
          300: '#80DEEA',
          400: '#4DD0E1',
          500: '#26C6DA',
          600: '#00BCD4',
          700: '#00ACC1',
          800: '#0097A7',
          900: '#00838F',
        }
      },
      fontFamily: {
      

        body: [
          'Bebas Neue',
          'Inter', 
          'ui-sans-serif', 
          'system-ui', 
          '-apple-system', 
          'system-ui', 
          'Segoe UI', 
          'Roboto', 
          'Helvetica Neue', 
          'Arial', 
          'Noto Sans', 
          'sans-serif', 
          'Apple Color Emoji', 
          'Segoe UI Emoji', 
          'Segoe UI Symbol', 
          'Noto Color Emoji'
        ],
        sans: [
          'Bebas Neue',
          'Inter', 
          'ui-sans-serif', 
          'system-ui', 
          '-apple-system', 
          'system-ui', 
          'Segoe UI', 
          'Roboto', 
          'Helvetica Neue', 
          'Arial', 
          'Noto Sans', 
          'sans-serif', 
          'Apple Color Emoji', 
          'Segoe UI Emoji', 
          'Segoe UI Symbol', 
          'Noto Color Emoji'
        ]
      },
      screens: {
        'xss': '280px',
        'xs': '320px',
        'sm': '375px',
        'sm-md': '600px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1440px',
      },
      width: {
        '1.5/12': '12.5%',  // Custom width between 1/12 and 2/12
      },
    },
  },
  variants: {},
  plugins: [],
  content: [
    './templates/**/*.html',
    './**/*.js',
    './**/*.jsx',
    './**/*.ts',
    './**/*.tsx',
    './static/css/**/*.css',
  ],
}
