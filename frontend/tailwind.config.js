/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        samsung: ['samsung-sharp-sans'],
        helvetica: ['helvetica-neue-55']
      }
    }
  },
  plugins: []
};
