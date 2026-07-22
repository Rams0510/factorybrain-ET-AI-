/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        industrial: {
          bg: "#0B1120",
          panel: "#111827",
          border: "#1F2937",
          accent: "#F59E0B",
          accent2: "#38BDF8",
          success: "#22C55E",
          danger: "#EF4444",
          warning: "#F59E0B",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
