<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const navigation = [
  { name: 'Dashboard', path: '/' },
  { name: 'Expenses', path: '/expenses' },
  { name: 'Categories', path: '/categories' },
  { name: 'Credit Cards', path: '/credit-cards' },
  { name: 'Debts', path: '/debts' },
  { name: 'Settings', path: '/settings' },
]
</script>

<template>
  <aside class="hidden lg:flex flex-col w-72 h-screen sticky top-0 border-r border-rule bg-paper/95 frosted">
    <div class="px-8 pt-10 pb-8">
      <span class="font-display text-xl font-semibold tracking-tight text-ink">Family Budget</span>
      <p class="text-xs text-muted mt-0.5">Household finance</p>
    </div>

    <nav class="flex-1 px-6 space-y-0.5">
      <router-link
        v-for="item in navigation"
        :key="item.path"
        :to="item.path"
        :class="[
          'group flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-all duration-200',
          route.path === item.path
            ? 'bg-accent/10 text-accent'
            : 'text-muted hover:text-ink hover:bg-paper-dark'
        ]"
      >
        <span
          class="w-1.5 h-1.5 rounded-full shrink-0"
          :class="route.path === item.path ? 'bg-accent' : 'bg-faint group-hover:bg-muted'"
        />
        {{ item.name }}
      </router-link>
    </nav>

    <div class="p-6 border-t border-rule">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-accent text-white flex items-center justify-center text-sm font-semibold shrink-0">
          {{ authStore.user?.full_name?.charAt(0) || 'U' }}
        </div>
        <div class="min-w-0">
          <p class="text-sm font-semibold truncate text-ink">{{ authStore.user?.full_name || 'Guest' }}</p>
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
