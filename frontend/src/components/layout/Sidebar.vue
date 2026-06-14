<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navigation = [
  { name: 'Dashboard', path: '/', index: '01' },
  { name: 'Expenses', path: '/expenses', index: '02' },
  { name: 'Categories', path: '/categories', index: '03' },
  { name: 'Credit Cards', path: '/credit-cards', index: '04' },
  { name: 'Debts', path: '/debts', index: '05' },
  { name: 'Settings', path: '/settings', index: '06' },
]
</script>

<template>
  <aside class="hidden lg:flex flex-col w-72 h-screen sticky top-0 border-r border-rule bg-paper">
    <div class="px-8 pt-10 pb-8">
      <div class="flex items-baseline gap-2">
        <span class="font-display text-2xl tracking-tight">Family Budget</span>
        <span class="w-1.5 h-1.5 rounded-full bg-accent" />
      </div>
      <p class="text-xs text-muted mt-1">Household finance journal</p>
    </div>

    <nav class="flex-1 px-6 space-y-1">
      <router-link
        v-for="item in navigation"
        :key="item.path"
        :to="item.path"
        :class="[
          'group flex items-baseline gap-4 px-4 py-3 rounded-xl transition-colors',
          route.path === item.path
            ? 'bg-paper-dark text-ink'
            : 'text-muted hover:text-ink hover:bg-paper-dark/50'
        ]"
      >
        <span
          class="text-xs font-semibold w-5"
          :class="route.path === item.path ? 'text-accent' : 'text-faint group-hover:text-muted'"
        >
          {{ item.index }}
        </span>
        <span class="text-sm font-medium">{{ item.name }}</span>
      </router-link>
    </nav>

    <div class="p-6 border-t border-rule">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-ink text-paper flex items-center justify-center text-sm font-semibold">
          {{ authStore.user?.full_name?.charAt(0) || 'U' }}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-semibold truncate">{{ authStore.user?.full_name || 'Guest' }}</p>
          <p class="text-xs text-muted truncate">{{ authStore.user?.email }}</p>
        </div>
      </div>
      <button
        @click="authStore.logout(); router.push('/login')"
        class="eb-btn eb-btn-ghost w-full text-xs"
      >
        Sign out
      </button>
    </div>
  </aside>
</template>
