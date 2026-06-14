import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category } from '@/types'
import api from '@/services/api'

export const useCategoryStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/categories')
      if (data.success) {
        categories.value = data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function createCategory(payload: { name: string; color?: string | null; icon?: string | null }) {
    const { data } = await api.post('/api/v1/categories', payload)
    if (data.success) {
      categories.value = [data.data, ...categories.value]
    }
    return data
  }

  return {
    categories,
    loading,
    fetchCategories,
    createCategory,
  }
})
