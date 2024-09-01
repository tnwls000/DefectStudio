/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        samsung: ['SamsungSharpSans'],
        helvetica: ['helvetica-neue-55'],
        Gmarket: ['GmarketSansMedium']
      }
    }
  },
  plugins: []
};
