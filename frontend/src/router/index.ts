import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Auth/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Auth/Register.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('@/components/layout/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard/Index.vue'),
        },
        {
          path: 'expenses',
          name: 'Expenses',
          component: () => import('@/views/Expenses/Index.vue'),
        },
        {
          path: 'categories',
          name: 'Categories',
          component: () => import('@/views/Categories/Index.vue'),
        },
        {
          path: 'credit-cards',
          name: 'CreditCards',
          component: () => import('@/views/CreditCards/Index.vue'),
        },
        {
          path: 'debts',
          name: 'Debts',
          component: () => import('@/views/Debts/Index.vue'),
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings/Index.vue'),
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

export default router
