import { defineStore } from 'pinia'
import { shallowRef, ref, computed } from 'vue'
import type { User } from '@/types'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = shallowRef<User | null>(null)
  const authReady = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  async function login(email: string, password: string) {
    const { data } = await api.post('/api/v1/auth/login', { email, password })
    if (data.success) {
      user.value = data.data
    }
  }

  async function logout() {
    try {
      await api.post('/api/v1/auth/logout')
    } finally {
      clearAuth()
    }
  }

  async function fetchCurrentUser() {
    try {
      const { data } = await api.get('/api/v1/auth/me')
      if (data.success) {
        user.value = data.data
      }
    } catch {
      user.value = null
    } finally {
      authReady.value = true
    }
  }

  function clearAuth() {
    user.value = null
  }

  return {
    user,
    authReady,
    isAuthenticated,
    login,
    logout,
    fetchCurrentUser,
    clearAuth,
  }
})
