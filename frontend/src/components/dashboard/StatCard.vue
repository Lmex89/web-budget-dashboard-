<script setup lang="ts">
import PaperCard from '@/components/ui/PaperCard.vue'
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    label: string
    value: string
    caption: string
    tone?: 'ink' | 'accent' | 'sage'
  }>(),
  { tone: 'ink' }
)

const valueClass = computed(() => ({
  'text-ink': props.tone === 'ink',
  'text-accent': props.tone === 'accent',
  'text-sage': props.tone === 'sage',
}))
</script>

<template>
  <PaperCard class="py-4 px-4 sm:p-5 md:p-6 animate-fade-up">
    <div class="flex items-center justify-between gap-4 sm:block">
      <div class="min-w-0 flex-1 sm:mb-0">
        <p class="text-xs font-bold uppercase tracking-widest text-muted">{{ label }}</p>
        <p class="text-sm text-muted mt-0.5 sm:hidden">{{ caption }}</p>
      </div>
      <p
        class="font-display text-2xl sm:text-4xl md:text-[2.75rem] leading-none tracking-tight shrink-0 tabular-nums"
        :class="valueClass"
      >
        {{ value }}
      </p>
    </div>
    <p class="text-sm text-muted mt-0.5 hidden sm:block">{{ caption }}</p>
  </PaperCard>
</template>
