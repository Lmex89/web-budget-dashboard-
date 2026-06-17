/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: "#ffffff",
          dark: "#0a0a0f",
        },
        card: {
          DEFAULT: "#f8f8fa",
          dark: "#14141f",
        },
        elevated: {
          DEFAULT: "#ffffff",
          dark: "#1c1c2e",
        },
        ink: {
          DEFAULT: "#0a0a0f",
          dark: "#f5f5f7",
        },
        muted: {
          DEFAULT: "#8e8e93",
          dark: "#636366",
        },
        accent: {
          blue: "#007aff",
          green: "#34c759",
          orange: "#ff9500",
          red: "#ff3b30",
          purple: "#af52de",
          teal: "#5ac8fa",
        },
        border: {
          DEFAULT: "#e5e5ea",
          dark: "#2c2c3a",
        },
      },
      fontFamily: {
        sans: ["System", "-apple-system", "Helvetica Neue", "sans-serif"],
        mono: ["Menlo", "monospace"],
      },
    },
  },
  plugins: [],
}
