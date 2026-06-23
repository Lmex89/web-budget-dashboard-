import { defineStore } from 'pinia'
import { shallowRef, ref } from 'vue'
import type { DashboardCategory } from '@/types'
import { fetchDashboardCategories } from '@/services/categories.service'

export const useDashboardCategoriesStore = defineStore('dashboard-categories', () => {
  const categories = shallowRef<DashboardCategory[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadCategories() {
    loading.value = true
    error.value = null
    try {
      categories.value = await fetchDashboardCategories()
    } catch (e) {
      error.value = 'Failed to load categories'
      throw e
    } finally {
      loading.value = false
    }
  }

  function getCategoryById(id: string): DashboardCategory | undefined {
    return categories.value.find((c) => c.id === id)
  }

  return {
    categories,
    loading,
    error,
    loadCategories,
    getCategoryById,
  }
})
