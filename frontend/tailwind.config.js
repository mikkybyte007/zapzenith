/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0F172A",
        surface: "#1E293B",
        primary: "#3B82F6",
        primaryHover: "#2563EB",
        textMain: "#F8FAFC",
        textMuted: "#94A3B8",
        messageSent: "#059669",
        messageReceived: "#334155",
      }
    },
  },
  plugins: [],
}
