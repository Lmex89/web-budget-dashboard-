import { defineStore } from 'pinia'
import { shallowRef, ref, computed } from 'vue'
import type { User, TokenResponse } from '@/types'
import api, { setStoredToken, clearStoredToken } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = shallowRef<User | null>(null)
  const authReady = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isMember = computed(() => user.value?.role === 'member')
  const isViewer = computed(() => user.value?.role === 'viewer')

  async function login(email: string, password: string) {
    const { data } = await api.post('/api/v1/auth/login', { email, password })
    if (data.success) {
      const tokenData = data.data as TokenResponse
      setStoredToken(tokenData.access_token)
      user.value = tokenData.user
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
    clearStoredToken()
  }

  return {
    user,
    authReady,
    isAuthenticated,
    isAdmin,
    isMember,
    isViewer,
    login,
    logout,
    fetchCurrentUser,
    clearAuth,
  }
})
