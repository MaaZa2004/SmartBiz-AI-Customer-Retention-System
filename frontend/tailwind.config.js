/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // Support toggling if needed, default dark
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#090D16',       // Darkest background
          card: '#111827',     // Premium grey-blue cards
          border: '#1F2937',   // Border lines
          accent: '#3B82F6',   // Primary brand blue
          accentHover: '#2563EB',
          text: '#F9FAFB',     // Bright text
          textMuted: '#9CA3AF' // Greyed text
        },
        success: '#10B981',    // Emerald green
        warning: '#F59E0B',    // Warm gold
        danger: '#EF4444',     // Vivid red
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'glow': '0 0 15px rgba(59, 130, 246, 0.15)',
        'glow-success': '0 0 15px rgba(16, 185, 129, 0.15)',
      }
    },
  },
  plugins: [],
}
