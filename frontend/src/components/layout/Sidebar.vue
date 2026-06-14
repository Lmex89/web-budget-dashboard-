<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navigation = [
  { name: 'Dashboard', path: '/', icon: '📊' },
  { name: 'Expenses', path: '/expenses', icon: '💰' },
  { name: 'Categories', path: '/categories', icon: '🏷️' },
      { name: 'Credit Cards', path: '/credit-cards', icon: '💳' },
      { name: 'Debts', path: '/debts', icon: '📋' },
      { name: 'Settings', path: '/settings', icon: '⚙️' },
]
</script>

<template>
  <div class="drawer-side z-40">
    <label for="drawer" class="drawer-overlay"></label>
    <aside class="bg-base-100 min-h-full w-72 lg:w-64 border-r border-base-200">
      <div class="flex items-center gap-3 px-6 py-5 border-b border-base-200">
        <div class="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-primary-content font-bold text-lg">
          FB
        </div>
        <div>
          <h2 class="font-semibold text-sm">Family Budget</h2>
          <p class="text-xs text-base-content/60">{{ authStore.user?.full_name }}</p>
        </div>
      </div>
      <nav class="p-4 space-y-1">
        <router-link
          v-for="item in navigation"
          :key="item.path"
          :to="item.path"
          :class="[
            'flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors',
            route.path === item.path
              ? 'bg-primary/10 text-primary'
              : 'text-base-content/70 hover:bg-base-200 hover:text-base-content'
          ]"
        >
          <span class="text-lg">{{ item.icon }}</span>
          {{ item.name }}
        </router-link>
      </nav>
      <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-base-200">
        <button
          @click="authStore.logout(); router.push('/login')"
          class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium text-base-content/70 hover:bg-base-200 w-full transition-colors"
        >
          <span class="text-lg">🚪</span>
          Logout
        </button>
      </div>
    </aside>
  </div>
</template>
