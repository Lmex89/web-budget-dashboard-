<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <header class="lg:hidden sticky top-0 z-30 bg-paper/90 backdrop-blur border-b border-rule">
    <div class="flex items-center justify-between px-5 h-14">
      <span class="font-display text-xl tracking-tight">Family Budget</span>
      <div
        class="w-8 h-8 rounded-full bg-ink text-paper flex items-center justify-center text-xs font-semibold"
      >
        {{ authStore.user?.full_name?.charAt(0) || 'U' }}
      </div>
    </div>
  </header>
</template>
