/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: 'var(--paper)',
        'paper-2': 'var(--paper-2)',
        'paper-dark': 'var(--paper-dark)',
        ink: 'var(--ink)',
        muted: 'var(--ink-muted)',
        faint: 'var(--ink-faint)',
        rule: 'var(--rule)',
        'rule-strong': 'var(--rule-strong)',
        accent: 'var(--accent)',
        'accent-light': 'var(--accent-light)',
        'accent-dark': 'var(--accent-dark)',
        sage: 'var(--sage)',
        'sage-light': 'var(--sage-light)',
        warn: 'var(--warn)',
        'warn-light': 'var(--warn-light)',
        danger: 'var(--danger)',
        'danger-light': 'var(--danger-light)',
        'cat-1': 'var(--cat-1)',
        'cat-2': 'var(--cat-2)',
        'cat-3': 'var(--cat-3)',
        'cat-4': 'var(--cat-4)',
        'cat-5': 'var(--cat-5)',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Text"', '"Helvetica Neue"', 'sans-serif'],
        display: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"Helvetica Neue"', 'sans-serif'],
      },
      boxShadow: {
        paper: 'var(--shadow-sm)',
        'paper-lg': 'var(--shadow-lg)',
      },
      borderRadius: {
        '2xl': 'var(--radius-lg)',
        xl: 'var(--radius-md)',
      },
      animation: {
        'fade-up': 'fadeUp 0.5s cubic-bezier(0.25, 0.1, 0.25, 1) both',
        'fade-in': 'fadeIn 0.35s cubic-bezier(0.25, 0.1, 0.25, 1) both',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
