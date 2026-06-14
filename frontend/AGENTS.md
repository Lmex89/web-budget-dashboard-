# Frontend AGENTS.md

See [root AGENTS.md](../AGENTS.md) for project overview. This file adds
frontend-specific instructions only.

## Fast commands

- Run dev server: `npm run dev`
- Build: `npm run build`
- Type check: `npm run typecheck` (alias: `npx vue-tsc --noEmit`)
- Docker dev: `docker compose up frontend` (uses `Dockerfile.dev`)
- Docker prod build: `docker build -f Dockerfile.prod -t frontend:prod .`

> **Note:** `npm run lint` is currently broken (missing `.gitignore` and ESLint config in this directory). Use `npm run typecheck` and `npm run build` for validation.

## Stack

- Vue 3 Composition API with `<script setup lang="ts">`
- Vite 5 (build tool)
- Tailwind CSS 3 + DaisyUI 4 (UI components — mostly legacy, custom design system preferred)
- Pinia (state management)
- Vue Router 4 (client-side routing, lazy-loaded routes)
- Axios (HTTP client with 401 interceptor)

## Design system

The app uses an **editorial/magazine** aesthetic with a mobile-first responsive layout.

### Typography

- **Display font**: `Bodoni Moda` (serif) — used for page titles, metric values, and section headings via `font-display` utility.
- **Body font**: `Sora` (sans-serif) — used for UI text via `font-sans` (default).
- Fonts are loaded from Google Fonts in `index.html`.

### Color palette (CSS variables)

All colors are defined as CSS custom properties in `src/style.css` and exposed as Tailwind color tokens in `tailwind.config.js`:

| Token | Usage |
|---|---|
| `paper` / `paper-2` / `paper-dark` | Backgrounds (warm cream tones) |
| `ink` / `muted` / `faint` | Text colors |
| `rule` / `rule-strong` | Borders and dividers |
| `accent` / `accent-light` / `accent-dark` | Primary accent (terracotta) |
| `sage` / `sage-light` | Secondary accent (muted green) |
| `warn` / `warn-light` | Warning state (amber) |
| `danger` / `danger-light` | Error/destructive state |

### Custom component classes

Use these instead of DaisyUI classes for new UI:

| Class | Purpose |
|---|---|
| `.eb-btn` + `.eb-btn-primary` / `.eb-btn-ghost` / `.eb-btn-accent` / `.eb-btn-danger` | Buttons |
| `.eb-input` / `.eb-select` | Form inputs |
| `.eb-label` | Form labels (uppercase, tracking-wide) |
| `.paper-card` / `.paper-card-filled` | Cards with border/shadow |
| `.chip` + `.chip-sage` / `.chip-accent` / `.chip-warn` / `.chip-muted` / `.chip-danger` | Status badges |
| `.progress-track` / `.progress-fill` | Progress bars |
| `.table-editorial` | Styled tables (desktop) |
| `.page-title` / `.page-subtitle` / `.eyebrow` / `.section-title` | Typography |
| `.animate-fade-up` / `.animate-fade-in` | Entry animations |
| `.animation-delay-100` through `.animation-delay-500` | Staggered animation delays |

### Layout

- **Mobile**: Sticky `MobileHeader` (top) + fixed `BottomNav` (6-tab bar). Main content has `pb-28` to clear the tab bar.
- **Desktop (lg+)**: Editorial `Sidebar` (left, 72px wide) with numbered nav links. No bottom nav.
- `MainLayout.vue` composes `Sidebar`, `MobileHeader`, and `BottomNav`.

### Shared components

Located in `src/components/ui/`:

| Component | Props | Purpose |
|---|---|---|
| `PageHeader` | `title`, `subtitle?`, `eyebrow?`, slot `action` | Page title block with optional action button |
| `PaperCard` | `filled?` | Styled card wrapper |
| `MetricCard` | `label`, `value`, `caption?`, `tone?` | Dashboard metric display |
| `EmptyState` | `title`, `description?`, slots `icon`, `action` | Empty data placeholder |
| `FormField` | `label`, `forId?`, `error?` | Label + slot for input |

### Formatting utilities

Use `src/utils/format.ts` for all data formatting:

- `formatCurrency(value)` — `$1,234.56`
- `formatDate(value)` — `Jan 15, 2026`
- `formatShortDate(value)` — `Jan 15`
- `formatMonthName(monthIndex)` — `January`

### Mobile-first patterns

- Tables on desktop (`hidden md:block`) become card lists on mobile (`md:hidden`).
- Forms stack vertically on mobile, use `grid-cols-2` or `grid-cols-3` on desktop.
- Touch targets: minimum 44px height for buttons and nav items.
- Bottom nav uses `pb-safe` utility for iPhone safe-area inset.
- Route `meta.title` is used for document title and mobile header.

## Key conventions

- **Auth**: JWT is HttpOnly cookie — JS cannot read it. The Pinia auth store calls `fetchCurrentUser()` on first load to determine auth state. The router guard uses `authStore.authReady` + `isAuthenticated`, NOT `document.cookie`.
- **Axios 401 interceptor**: Clears auth state only (no `window.location.href` redirect to avoid reload loop). Redirect is handled by the router guard.
- **Routes**: Lazy-loaded via dynamic `import()`. Protected routes use `beforeEach` guard. Each route has `meta.title` for document title.
- **No comments in code** unless explicitly requested.
- **Debt API shape**: Keep debt request/response fields aligned with backend schema names (`original_amount`, `remaining_amount`, `counterparty_name`, `type`, `status`) instead of introducing frontend-only aliases.

## Reactivity and TypeScript conventions

- **Prefer `shallowRef` over `ref`** for data that is replaced entirely (arrays, objects from API). Use `ref` only when deep reactivity is needed (e.g., form objects with v-model).
- **Pinia stores**: Use `shallowRef` for lists and API response objects. Use `ref` for boolean flags like `loading`.
- **Type everything**: Define interfaces in `src/types/index.ts` for all API payloads and responses. Avoid `any` types.
- **Composables**: Extract reusable logic into `src/composables/`. The `useForm` composable handles form state, submission, and error handling.
- **Debt API shape**: Keep debt request/response fields aligned with backend schema names (`original_amount`, `remaining_amount`, `counterparty_name`, `type`, `status`) instead of introducing frontend-only aliases.

## Available skills

Skills under `.agents/skills/` are loaded on demand:

| Skill | When to use |
|---|---|
| `vue-best-practices` | Any `.vue` file work |
| `vue-debug-guides` | Debugging runtime errors, reactivity, SSR issues |
| `vue-pinia-best-practices` | Pinia store creation or modification |
| `vue` | Composition API reference, `<script setup>` macros |
| `tailwind-css-patterns` | Styling, layout, responsive design |
| `typescript-advanced-types` | Complex TS types, generics, type guards |
| `vite` | Vite config or build issues |
| `accessibility` | WCAG compliance, ARIA, keyboard nav |
| `seo` | Meta tags, structured data, sitemaps |
| `frontend-design` | UI direction, avoiding generic design |

## Project structure

```
frontend/src/
├── main.ts            # App entry
├── App.vue            # Root component
├── router/index.ts    # Routes + guard + meta.title
├── services/api.ts    # Axios instance + interceptors
├── stores/
│   ├── auth.ts        # Auth state (login, logout, fetchCurrentUser)
│   ├── categories.ts  # Category list/create
│   ├── creditCards.ts # Credit card list/create
│   ├── debts.ts       # Debt list/create
│   └── expenses.ts    # Expense CRUD + analytics
├── composables/
│   └── useForm.ts     # Reusable form state management
├── components/
│   ├── layout/        # MainLayout, MobileHeader, BottomNav, Sidebar
│   └── ui/            # PageHeader, PaperCard, MetricCard, EmptyState, FormField
├── views/
│   ├── Auth/          # Login, Register
│   ├── Dashboard/
│   ├── Expenses/
│   ├── Categories/
│   ├── CreditCards/
│   ├── Debts/
│   └── Settings/
├── utils/
│   └── format.ts      # Currency, date, month formatting
├── types/index.ts     # Shared TS interfaces
└── style.css          # Tailwind imports + design tokens + component classes
```

## Creating a new view

1. Add `.vue` file in `src/views/<Name>/Index.vue`
2. Add route in `src/router/index.ts` (lazy import, `meta: { requiresAuth: true, title: 'Page Name' }`)
3. Create Pinia store in `src/stores/` if state is shared
4. Add API methods in `src/services/api.ts` if new endpoints are needed
5. Add entry to `BottomNav.vue` navigation array for mobile access
6. Use `PageHeader`, `PaperCard`, `FormField`, and `EmptyState` components
7. Use `format.ts` utilities for all currency/date display
8. Provide mobile card list + desktop table pattern for data lists
9. Use `useForm` composable for form state management
10. Define TypeScript interfaces in `src/types/index.ts` for all API payloads
