<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<template>
  <PaperCard class="p-10 md:p-14 text-center animate-fade-up">
    <div class="w-12 h-12 mx-auto rounded-full bg-paper-dark flex items-center justify-center text-2xl mb-4">
      <slot name="icon" />
    </div>
    <h3 class="section-title">{{ title }}</h3>
    <p v-if="description" class="text-sm text-muted mt-2 max-w-xs mx-auto">{{ description }}</p>
    <div v-if="$slots.action" class="mt-5">
      <slot name="action" />
    </div>
  </PaperCard>
</template>
