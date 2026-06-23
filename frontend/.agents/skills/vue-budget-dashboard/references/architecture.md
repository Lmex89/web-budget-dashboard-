# Architecture

## Folder structure

```
src/
├── main.ts
├── App.vue
├── router/
│   └── index.ts
├── stores/
│   ├── expenses.store.ts
│   ├── categories.store.ts
│   └── auth.store.ts
├── services/
│   ├── http.ts              # axios instance + interceptors
│   ├── expenses.service.ts
│   └── categories.service.ts
├── composables/
│   ├── useCurrency.ts
│   └── usePagination.ts
├── components/
│   ├── base/                # Button, Card, Select, Badge, Modal
│   ├── dashboard/            # CategoryDistribution, RecentExpenses, StatCard
│   └── layout/               # Sidebar, TopBar
├── views/
│   ├── DashboardView.vue
│   ├── ExpensesView.vue
│   └── CategoriesView.vue
├── types/
│   └── domain.ts             # Expense, Category, FamilyMember interfaces
└── utils/
    └── format.ts
```

## Axios service layer (`src/services/http.ts`)

```ts
import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10_000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      // route to login, clear session
    }
    return Promise.reject(error)
  },
)
```

Each domain gets its own service module that only this layer touches:

```ts
// src/services/expenses.service.ts
import { http } from './http'
import type { Expense } from '@/types/domain'

export const expensesService = {
  list: (params: { month: number; year: number; categoryId?: string }) =>
    http.get<Expense[]>('/expenses', { params }).then((r) => r.data),
  create: (payload: Omit<Expense, 'id'>) =>
    http.post<Expense>('/expenses', payload).then((r) => r.data),
}
```

## Pinia store (setup syntax, typed)

```ts
// src/stores/expenses.store.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { expensesService } from '@/services/expenses.service'
import type { Expense } from '@/types/domain'

export const useExpensesStore = defineStore('expenses', () => {
  const items = ref<Expense[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const total = computed(() =>
    items.value.reduce((sum, e) => sum + e.amount, 0),
  )

  async function fetchExpenses(month: number, year: number) {
    isLoading.value = true
    error.value = null
    try {
      items.value = await expensesService.list({ month, year })
    } catch (e) {
      error.value = 'Could not load expenses. Try again.'
    } finally {
      isLoading.value = false
    }
  }

  return { items, isLoading, error, total, fetchExpenses }
})
```

Rules: every store exposes loading/error state for its async actions; components
read these to drive skeletons and error banners, never inline `try/catch` in a
`.vue` file.

## Router (`src/router/index.ts`)

```ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    title?: string
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true, title: 'Overview' },
  },
  {
    path: '/expenses',
    name: 'expenses',
    component: () => import('@/views/ExpensesView.vue'),
    meta: { requiresAuth: true, title: 'Expenses' },
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} — Family Budget` : 'Family Budget'
})
```

Always lazy-load route components (`() => import(...)`) — never static imports in
the routes array, that defeats code-splitting from day one.
