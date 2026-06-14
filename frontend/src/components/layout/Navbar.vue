<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { useRoute } from 'vue-router'

const authStore = useAuthStore()
const route = useRoute()
</script>

<template>
  <div class="navbar bg-base-100 border-b border-base-200 lg:hidden">
    <div class="flex-none">
      <label for="drawer" class="btn btn-square btn-ghost">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block w-6 h-6 stroke-current">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
      </label>
    </div>
    <div class="flex-1">
      <span class="text-sm font-semibold capitalize">{{ route.name }}</span>
    </div>
    <div class="flex-none gap-2">
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="avatar placeholder btn btn-ghost btn-circle">
          <div class="w-8 rounded-full bg-primary text-primary-content text-xs font-bold">
            {{ authStore.user?.full_name?.charAt(0) || 'U' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
