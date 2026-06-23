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
- Tailwind CSS 3 (custom design system, no DaisyUI)
- Pinia (state management)
- Vue Router 4 (client-side routing, lazy-loaded routes)
- Axios (HTTP client with 401 interceptor)

## Design system

The app uses an **Apple/minimal** aesthetic with a mobile-first responsive layout. Supports automatic dark mode via `prefers-color-scheme`.

### Typography

- **Font**: System font stack (`-apple-system`, `SF Pro`, `Helvetica Neue`) used for both display and body text via `font-display` and `font-sans` utilities.
- No external font loading — relies on OS-native system fonts.
- Display text uses bold (700) weight with tight tracking; body text uses regular (400) weight.

### Color palette (CSS variables)

All colors are defined as CSS custom properties in `src/style.css` with automatic dark mode support, and exposed as Tailwind color tokens in `tailwind.config.js`:

| Token | Light | Dark | Usage |
|---|---|---|---|
| `paper` | `#ffffff` | `#000000` | Primary background |
| `paper-2` | `#fafafa` | `#1c1c1e` | Secondary surface |
| `paper-dark` | `#f5f5f7` | `#2c2c2e` | Tertiary surface |
| `ink` | `#1d1d1f` | `#f5f5f7` | Primary text |
| `muted` | `#86868b` | `#98989d` | Secondary text |
| `faint` | `#aeaeb2` | `#636366` | Placeholder/disabled |
| `rule` | `#d2d2d7` | `#38383a` | Hairline borders |
| `rule-strong` | `#c7c7cc` | `#48484a` | Strong borders |
| `accent` | `#0071e3` | `#0a84ff` | Primary accent (blue) |
| `sage` | `#34c759` | `#30d158` | Positive/success |
| `warn` | `#ff9500` | `#ff9f0a` | Warning state |
| `danger` | `#ff3b30` | `#ff453a` | Error/destructive |

### Custom component classes

Use these instead of DaisyUI classes for new UI (DaisyUI was removed):

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
| `.frosted` | Frosted glass effect via `backdrop-filter: blur(20px)` |

### Layout

- **Mobile**: Sticky `MobileHeader` (top) + fixed `BottomNav` (6-tab bar). Main content has `pb-28` to clear the tab bar.
- **Desktop (lg+)**: Editorial `Sidebar` (left, 220px wide) with dot nav links. No bottom nav.
- `MainLayout.vue` composes `Sidebar`, `MobileHeader`, and `BottomNav`.

### Shared components

Located in `src/components/ui/`:

| Component | Props | Purpose |
|---|---|---|
| `PageHeader` | `title`, `subtitle?`, `eyebrow?`, slot `action` | Page title block with optional action button |
| `PaperCard` | `filled?` | Styled card wrapper (uses `isolate` not `overflow-hidden` to avoid clipping date pickers) |
| `MetricCard` | `label`, `value`, `caption?`, `tone?` | Dashboard metric display |
| `StatCard` | `label`, `value`, `caption`, `tone?` | Mobile-first stat row/card |
| `CategoryStackedBar` | `segments`, `total-label`, `loading`, `error` | Horizontal stacked bar with legend |
| `RecentExpensesCard` | `expenses`, `loading`, `error` | Expense list card |
| `TopCategoriesCard` | `categories`, `loading`, `error` | Top categories list card |
| `EmptyState` | `title`, `description?`, slots `icon`, `action` | Empty data placeholder |
| `FormField` | `label`, `forId?`, `error?` | Label + slot for input |

### Formatting utilities

Use `src/utils/format.ts` for all data formatting:

- `formatCurrency(value)` — `$1,234.56`
- `formatDate(value)` — `Jan 15, 2026`
- `formatShortDate(value)` — `Jan 15`
- `formatMonthName(monthIndex)` — `January`

Composables in `src/composables/`:

- `useCurrency()` — returns `formatCurrency` via `Intl.NumberFormat`
- `useForm()` — form state, submission, and error handling

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
|---|---|---|
| `vue-budget-dashboard` | Building budget/finance dashboard features, UI proposals for finance domain, scaffolding or theming Vue budget apps |
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
├── services/
│   └── api.ts              # Axios instance + interceptors
├── stores/
│   ├── auth.ts        # Auth state (login, logout, fetchCurrentUser)
│   ├── categories.ts  # Category list/create/update
│   ├── creditCards.ts # Credit card list/create
│   ├── debts.ts       # Debt list/create
│   └── expenses.ts    # Expense CRUD + analytics
├── composables/
│   ├── useCurrency.ts  # Intl.NumberFormat currency formatter
│   └── useForm.ts      # Reusable form state management
├── components/
│   ├── dashboard/     # StatCard, CategoryStackedBar, RecentExpensesCard, TopCategoriesCard
│   ├── layout/        # MainLayout, MobileHeader, BottomNav, Sidebar
│   └── ui/            # PageHeader, PaperCard, MetricCard, EmptyState, FormField
├── views/
│   ├── Auth/          # Login, Register
│   ├── Dashboard/     # Legacy dashboard (superseded by DashboardView.vue)
│   ├── Expenses/
│   ├── Categories/    # Category list with inline name editing
│   ├── CreditCards/
│   ├── Debts/
│   ├── Settings/
│       └── DashboardView.vue  # Mobile-first overview (uses real expense + category stores)
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
