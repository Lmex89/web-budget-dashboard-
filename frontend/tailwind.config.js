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
      },
      fontFamily: {
        sans: ['Sora', 'system-ui', 'sans-serif'],
        display: ['"Bodoni Moda"', 'Georgia', 'serif'],
      },
      boxShadow: {
        paper: 'var(--shadow-md)',
        'paper-lg': 'var(--shadow-lg)',
      },
      borderRadius: {
        '2xl': 'var(--radius-lg)',
        xl: 'var(--radius-md)',
      },
      animation: {
        'fade-up': 'fadeUp 0.7s var(--ease-out-expo) both',
        'fade-in': 'fadeIn 0.5s var(--ease-out-expo) both',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light"],
  },
}
