<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()

const nav = [
  {
    name: 'Home',
    short: 'Home',
    path: '/',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6zM3.75 15.75A2.25 2.25 0 016 13.5h2.25a2.25 2.25 0 012.25 2.25V18a2.25 2.25 0 01-2.25 2.25H6A2.25 2.25 0 013.75 18v-2.25zM13.5 6a2.25 2.25 0 012.25-2.25H18A2.25 2.25 0 0120.25 6v2.25A2.25 2.25 0 0118 10.5h-2.25a2.25 2.25 0 01-2.25-2.25V6zM13.5 15.75a2.25 2.25 0 012.25-2.25H18a2.25 2.25 0 012.25 2.25V18A2.25 2.25 0 0118 20.25h-2.25A2.25 2.25 0 0113.5 18v-2.25z" /></svg>`,
  },
  {
    name: 'Expenses',
    short: 'Spend',
    path: '/expenses',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v.375c0 .621.504 1.125 1.125 1.125H4.5m0 0V6A2.25 2.25 0 016 3.75h.75m-1.5 15H6a2.25 2.25 0 01-2.25-2.25V6m3 0V4.5A2.25 2.25 0 016 2.25h.75m1.5 15V18a2.25 2.25 0 01-2.25 2.25H6M17.25 18.75V5.25m0 13.5a2.25 2.25 0 01-2.25-2.25V6m2.25 13.5V18a2.25 2.25 0 012.25-2.25h.75M20.25 6h.75a2.25 2.25 0 012.25 2.25v.75m-3 0V4.5a2.25 2.25 0 012.25-2.25h.75" /></svg>`,
  },
  {
    name: 'Categories',
    short: 'Tags',
    path: '/categories',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.671 9.671c.404.404.997.607 1.591.607h4.318A2.25 2.25 0 0022 19.05V14.75a2.25 2.25 0 00-.659-1.591l-6.997-6.997A2.25 2.25 0 0012.568 4.5l-2.95-2.95A2.25 2.25 0 007.068 3H9.568z" /><path stroke-linecap="round" stroke-linejoin="round" d="M6 9h.008v.008H6V9z" /></svg>`,
  },
  {
    name: 'Credit Cards',
    short: 'Cards',
    path: '/credit-cards',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-12.75-4.5v9.75c0 1.036.84 1.875 1.875 1.875h16.5A1.875 1.875 0 0021.375 18V9m-19.5 0V5.625A2.625 2.625 0 014.875 3h14.25a2.625 2.625 0 012.625 2.625V9m-19.5 0h19.5" /></svg>`,
  },
  {
    name: 'Debts',
    short: 'Debts',
    path: '/debts',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" /></svg>`,
  },
  {
    name: 'Family',
    short: 'Family',
    path: '/settings',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" /></svg>`,
  },
]
</script>

<template>
  <nav
    class="lg:hidden fixed bottom-0 inset-x-0 z-40 frosted bg-paper/80 border-t border-rule pb-safe"
  >
    <div class="grid grid-cols-6 h-16">
      <router-link
        v-for="item in nav"
        :key="item.path"
        :to="item.path"
        :aria-label="item.name"
        class="bottom-nav-link pt-1"
        :class="{ active: route.path === item.path }"
        v-html="item.icon + '<span>' + item.short + '</span>'"
      />
    </div>
  </nav>
</template>
