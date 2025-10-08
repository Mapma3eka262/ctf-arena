/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{html,js}",
  ],
  theme: {
    extend: {
      colors: {
        ctf: {
          primary: '#1e40af',
          secondary: '#dc2626',
          success: '#16a34a',
          warning: '#d97706',
          danger: '#dc2626'
        }
      }
    },
  },
  plugins: [],
}