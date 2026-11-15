/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        navy: {
          950: "#060B19",
          900: "#0B132B",
          850: "#111B38",
          800: "#1C2541",
          700: "#273457",
          600: "#3A506B",
          500: "#4F6D7A",
        },
        accent: {
          cyan: "#5BC0BE",
          indigo: "#6366F1",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#F43F5E"
        }
      }
    },
  },
  plugins: [],
}
