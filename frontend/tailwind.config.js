/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx}", // Incluye todos los archivos JS/JSX en src/
  ],
  theme: {
    extend: {
      colors: {
        'noir-eclipse': '#003366', // Azul oscuro
        'obsidian-wave': '#141920', // Fondo oscuro
        'lime-light': '#C8FD7C', // Cambiado de #00ff00 a #C8FD7C
        'royal-nebula': '#2a4066', // Bordes
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'], // SF Pro
      },
    },
  },
  plugins: [],
};