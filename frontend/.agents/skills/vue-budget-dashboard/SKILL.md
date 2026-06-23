---
name: vue-budget-dashboard
description: Build family/personal budget and finance dashboards using Vue 3 (Composition API, script setup, TypeScript), Vite 5, Tailwind CSS 3 with a custom design system (no DaisyUI/component libraries), Pinia, Vue Router 4, and Axios. Use this whenever the user asks for a budget dashboard, expense tracker, finance overview, spending dashboard, or wants UI proposals/mockups for that domain in this exact stack. Also trigger for requests to scaffold, restructure, or theme an existing Vue budget app, even if they only mention "dashboard" without naming the stack — check project files for vue+vite+tailwind signals first.
---

# Vue Budget Dashboard

Builds personal/family finance dashboards on a fixed stack: Vue 3 Composition API
(`<script setup lang="ts">` only, no Options API), Vite 5, TypeScript, Tailwind CSS 3
with a hand-rolled design system (no DaisyUI, no Headless UI, no component kits),
Pinia, Vue Router 4, Axios.

## When generating proposals (no code yet)

If the user wants design proposals/mockups rather than a working app, use the
`visualize` tool (HTML mode) to render each proposal as a static preview, not real
Vue SFCs — proposals are for visual sign-off, code comes after. Each proposal must
differ on a real axis (layout density, data hierarchy, navigation model), never just
color swaps. See `references/design-proposals.md` for the 3-proposal framework and
how to ground each one in actual budget-dashboard content (categories, recent
transactions, totals, family members).

## When building the real app

1. Read `references/architecture.md` for folder structure, Pinia store shape, Axios
   service layer pattern, and router setup before writing any file.
2. Read `references/tailwind-tokens.md` for the token-based Tailwind config approach
   (CSS variables → `tailwind.config.ts` → no inline magic hex values in components).
3. Read `references/components.md` for the base component contract (props/emits
   conventions, no logic in templates beyond simple expressions, composables for
   shared logic).

## Hard constraints (never violate)

- No Options API, no `data()`/`methods` — `<script setup lang="ts">` everywhere.
- No DaisyUI, Bootstrap, Vuetify, PrimeVue, or any pre-built component kit. Every
  component (Button, Card, Select, Modal) is hand-built against the token system.
- No business logic inside `.vue` template blocks beyond a ternary or simple format
  call — push it to a computed property or composable.
- Pinia stores use `defineStore` with the **setup syntax** (function body, not the
  options object), and state is typed via interfaces, never `any`.
- Axios calls never appear directly inside components — always through a typed
  service module (`src/services/*.ts`) that a store or composable calls.
- Currency, date, and number formatting go through shared utils
  (`src/utils/format.ts`), never ad-hoc `toFixed()` calls scattered in components.
- Every interactive element has a visible focus state and meets WCAG AA contrast —
  check this explicitly for dark-theme palettes, where low-contrast grays are the
  most common failure.

## Domain vocabulary (keep consistent across components and copy)

Categories, Expenses, Recent expenses, Total expenses, Family members, Credit Cards,
Debts. Money is always shown with currency symbol and two decimals. Dates are
relative within 7 days ("Jun 22"), absolute beyond that. Empty states say what to do
next ("Add your first expense"), never "No data."
