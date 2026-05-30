/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        atlas: {
          ink: "#101820",
          paper: "#f6efe3",
          moss: "#455b3e",
          brass: "#c18f3a",
          river: "#2d6f88",
          danger: "#b84634"
        }
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body: ["Avenir Next", "Nunito Sans", "sans-serif"]
      },
      boxShadow: {
        panel: "0 24px 80px rgba(16, 24, 32, 0.18)"
      }
    }
  },
  plugins: []
};
