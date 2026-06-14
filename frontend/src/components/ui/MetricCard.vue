<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string
    value: string
    caption?: string
    tone?: 'ink' | 'accent' | 'sage'
  }>(),
  { tone: 'ink' }
)
</script>

<template>
  <PaperCard class="p-5 md:p-6 animate-fade-up">
    <p class="text-xs font-bold uppercase tracking-widest text-muted">{{ label }}</p>
    <p
      class="font-display text-4xl md:text-[2.75rem] leading-none tracking-tight mt-3"
      :class="{
        'text-ink': tone === 'ink',
        'text-accent': tone === 'accent',
        'text-sage': tone === 'sage',
      }"
    >
      {{ value }}
    </p>
    <p v-if="caption" class="text-sm text-muted mt-2">{{ caption }}</p>
  </PaperCard>
</template>
