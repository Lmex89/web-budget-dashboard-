import { beforeEach, describe, expect, it, vi } from 'vitest'
import { flushPromises, mount } from '@vue/test-utils'
import { createPinia, setActivePinia, type Pinia } from 'pinia'
import MobileHeader from '@/components/layout/MobileHeader.vue'
import { useAuthStore } from '@/stores/auth'

const mocks = vi.hoisted(() => ({
  post: vi.fn(),
  push: vi.fn(),
  clearStoredToken: vi.fn(),
  setStoredToken: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mocks.push }),
}))

vi.mock('@/services/api', () => ({
  default: { post: mocks.post },
  clearStoredToken: mocks.clearStoredToken,
  setStoredToken: mocks.setStoredToken,
}))

describe('MobileHeader logout', () => {
  let pinia: Pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    mocks.post.mockResolvedValue({ data: { success: true } })
    mocks.push.mockResolvedValue(undefined)
    mocks.clearStoredToken.mockClear()
    mocks.push.mockClear()
  })

  it('logs out and redirects when the avatar is clicked', async () => {
    const authStore = useAuthStore()
    authStore.user = {
      id: 'user-1',
      email: 'alex@example.com',
      full_name: 'Alex',
      is_active: true,
      role: 'member',
      family_id: 'family-1',
      created_at: '2026-01-01T00:00:00Z',
    }

    const wrapper = mount(MobileHeader, {
      global: { plugins: [pinia] },
    })

    const avatar = wrapper.get('button[aria-label="Sign out"]')
    await avatar.trigger('click')
    await flushPromises()

    expect(mocks.post).toHaveBeenCalledWith('/api/v1/auth/logout')
    expect(authStore.user).toBeNull()
    expect(mocks.clearStoredToken).toHaveBeenCalledOnce()
    expect(mocks.push).toHaveBeenCalledWith('/login')
  })
})
