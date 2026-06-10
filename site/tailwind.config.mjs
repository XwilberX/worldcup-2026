/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{astro,html,js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        fifa: {
          blue: "#1a237e",
          gold: "#b8942d",
          bg: "#f5f6fa",
        },
      },
    },
  },
  plugins: [],
};
