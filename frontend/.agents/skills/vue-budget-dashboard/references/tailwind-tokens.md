# Tailwind Token System

No DaisyUI. No prebuilt themes. Colors and spacing come from CSS variables defined
once, then wired into `tailwind.config.ts` as semantic names. Components reference
the semantic names, never raw hex or raw Tailwind grays.

## CSS variables (`src/styles/tokens.css`)

```css
:root {
  /* surfaces */
  --surface-base: 10 10 12;       /* near-black page bg */
  --surface-raised: 20 20 24;     /* card bg */
  --surface-hover: 28 28 33;

  /* text */
  --text-primary: 245 245 247;
  --text-secondary: 161 161 170;
  --text-tertiary: 113 113 122;

  /* brand / data */
  --accent: 59 130 246;           /* blue — primary actions, links */
  --positive: 34 197 94;          /* family/sharing, healthy balance */
  --warning: 234 179 8;
  --danger: 239 68 68;

  /* category palette — fixed, cycled, never random */
  --cat-1: 249 115 22;  /* orange */
  --cat-2: 59 130 246;  /* blue */
  --cat-3: 34 197 94;   /* green */
  --cat-4: 168 85 247;  /* purple */
  --cat-5: 236 72 153;  /* pink */

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
}
```

Use RGB triplets (no `#`) so Tailwind's `rgb(var(--x) / <alpha-value>)` opacity
syntax works.

## `tailwind.config.ts`

```ts
import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{vue,ts}'],
  theme: {
    extend: {
      colors: {
        surface: {
          base: 'rgb(var(--surface-base) / <alpha-value>)',
          raised: 'rgb(var(--surface-raised) / <alpha-value>)',
          hover: 'rgb(var(--surface-hover) / <alpha-value>)',
        },
        text: {
          primary: 'rgb(var(--text-primary) / <alpha-value>)',
          secondary: 'rgb(var(--text-secondary) / <alpha-value>)',
          tertiary: 'rgb(var(--text-tertiary) / <alpha-value>)',
        },
        accent: 'rgb(var(--accent) / <alpha-value>)',
        positive: 'rgb(var(--positive) / <alpha-value>)',
        warning: 'rgb(var(--warning) / <alpha-value>)',
        danger: 'rgb(var(--danger) / <alpha-value>)',
        cat: {
          1: 'rgb(var(--cat-1) / <alpha-value>)',
          2: 'rgb(var(--cat-2) / <alpha-value>)',
          3: 'rgb(var(--cat-3) / <alpha-value>)',
          4: 'rgb(var(--cat-4) / <alpha-value>)',
          5: 'rgb(var(--cat-5) / <alpha-value>)',
        },
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'], // amounts, ids
      },
    },
  },
  plugins: [],
} satisfies Config
```

## Usage rule

`bg-surface-raised`, `text-text-secondary`, `border-cat-2/40` — always semantic
classes. If a new color is needed, add a variable first, never drop a raw hex into
a component. This is what makes re-theming (e.g. light mode, white-label) a one-file
change instead of a grep-and-replace across the app.

## Category color assignment

Categories cycle through `cat-1`..`cat-5` by **insertion order**, stored as an index
on the category record server-side — never re-derived client-side by string hash,
or colors shift when categories are renamed/reordered.
