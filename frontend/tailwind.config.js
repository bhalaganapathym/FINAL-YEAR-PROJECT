/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Space Grotesk"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        neo: {
          bg: '#FFFDF5',
          black: '#000000',
          white: '#FFFFFF',
          accent: '#FF6B6B',     // Hot Red
          secondary: '#FFD93D',  // Vivid Yellow
          muted: '#C4B5FD',      // Soft Violet
          emerald: '#10B981',    // Vivid Green
          blue: '#38BDF8',       // Bright Sky Blue
        },
      },
      boxShadow: {
        'neo-sm': '4px 4px 0px 0px #000000',
        'neo': '6px 6px 0px 0px #000000',
        'neo-md': '8px 8px 0px 0px #000000',
        'neo-lg': '12px 12px 0px 0px #000000',
        'neo-xl': '16px 16px 0px 0px #000000',
      },
      borderWidth: {
        '3': '3px',
        '4': '4px',
        '6': '6px',
        '8': '8px',
      },
    },
  },
  plugins: [],
}
