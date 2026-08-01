/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        background: '#F5F0EB',
        foreground: '#1A1A1A',
        primary: '#2563EB',
        accent: '#059669',
        muted: '#737373',
        border: '#E5E5E5',
        card: '#FFFFFF',
        danger: '#DC2626',
        warning: '#D97706',
      },
      borderRadius: {
        DEFAULT: '6px',
        sm: '4px',
        md: '6px',
        lg: '8px',
      },
    },
  },
  plugins: [],
};
