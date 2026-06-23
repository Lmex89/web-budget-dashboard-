import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Auth/Login.vue'),
      meta: { requiresAuth: false, title: 'Sign in' },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Auth/Register.vue'),
      meta: { requiresAuth: false, title: 'Create account' },
    },
    {
      path: '/',
      component: () => import('@/components/layout/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: 'Overview' },
        },
        {
          path: 'expenses',
          name: 'Expenses',
          component: () => import('@/views/Expenses/Index.vue'),
          meta: { title: 'Expenses' },
        },
        {
          path: 'categories',
          name: 'Categories',
          component: () => import('@/views/Categories/Index.vue'),
          meta: { title: 'Categories' },
        },
        {
          path: 'credit-cards',
          name: 'CreditCards',
          component: () => import('@/views/CreditCards/Index.vue'),
          meta: { title: 'Credit Cards' },
        },
        {
          path: 'debts',
          name: 'Debts',
          component: () => import('@/views/Debts/Index.vue'),
          meta: { title: 'Debts' },
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings/Index.vue'),
          meta: { title: 'Family' },
        },
      ],
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()

  if (!auth.authReady) {
    await auth.fetchCurrentUser()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && auth.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

router.afterEach((to) => {
  const title = to.meta.title as string | undefined
  document.title = title ? `${title} · Family Budget` : 'Family Budget'
})

export default router
