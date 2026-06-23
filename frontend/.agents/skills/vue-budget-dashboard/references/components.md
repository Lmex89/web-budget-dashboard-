# Component Conventions

## Base component contract

Every `components/base/*` component:
- Typed `Props` interface, `defineProps<Props>()` — no runtime prop validators.
- Emits typed via `defineEmits<{ ... }>()`.
- No default exports of options objects — `<script setup>` only.
- Visual variants via a `variant` prop (`'primary' | 'secondary' | 'ghost'`), not
  separate components per variant.

Example — `StatCard.vue`:

```vue
<script setup lang="ts">
interface Props {
  label: string
  value: string
  trend?: { direction: 'up' | 'down'; label: string }
  accent?: 'default' | 'accent' | 'positive'
}

withDefaults(defineProps<Props>(), { accent: 'default' })
</script>

<template>
  <div class="rounded-lg bg-surface-raised p-5">
    <p class="text-xs font-medium uppercase tracking-wide text-text-tertiary">
      {{ label }}
    </p>
    <p
      class="mt-2 text-3xl font-semibold"
      :class="accent === 'accent' ? 'text-accent' : accent === 'positive' ? 'text-positive' : 'text-text-primary'"
    >
      {{ value }}
    </p>
    <p v-if="trend" class="mt-1 text-xs text-text-secondary">{{ trend.label }}</p>
  </div>
</template>
```

## Composables over mixins/utils-with-state

Any logic touching reactive state and reused across 2+ components becomes a
composable, not a utility function with module-level `ref()`s (that creates
accidental shared state across component instances unless explicitly intended).

```ts
// src/composables/useCurrency.ts
export function useCurrency(locale = 'en-US', currency = 'USD') {
  const formatter = new Intl.NumberFormat(locale, { style: 'currency', currency })
  return { format: (value: number) => formatter.format(value) }
}
```

## List rendering

Always `:key` with a stable id, never index, for any list backed by API data
(expenses, categories) — index keys break Vue's reuse logic on reorder/filter and
cause input state to leak between rows.

## Loading and empty states

Every data-bearing component handles three states explicitly: loading (skeleton,
not a spinner-only overlay for list/card content), empty (actionable message), and
error (retry affordance). Never render a bare empty array as a missing section.
