<script setup lang="ts">
defineProps<{
  label: string
  forId?: string
  error?: string
}>()
</script>

<template>
  <div class="flex flex-col gap-1.5">
    <label v-if="label" :for="forId" class="eb-label">{{ label }}</label>
    <slot />
    <p v-if="error" class="text-xs font-medium text-danger">{{ error }}</p>
  </div>
</template>
