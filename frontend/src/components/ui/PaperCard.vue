<script setup lang="ts">
defineProps<{
  filled?: boolean
}>()
</script>

<template>
  <div :class="filled ? 'paper-card-filled' : 'paper-card'">
    <slot />
  </div>
</template>
