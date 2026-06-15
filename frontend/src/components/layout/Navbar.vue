<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRoute } from 'vue-router'

const authStore = useAuthStore()
const route = useRoute()
</script>

<template>
  <div class="lg:hidden flex items-center h-14 px-5 border-b border-rule bg-paper/80 frosted">
    <div class="flex-1">
      <span class="text-sm font-semibold text-ink capitalize">{{ route.name }}</span>
    </div>
    <div class="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center text-xs font-semibold">
      {{ authStore.user?.full_name?.charAt(0) || 'U' }}
    </div>
  </div>
</template>
