import { defineStore } from 'pinia'
import { shallowRef, ref } from 'vue'
import type { Category, CreateCategoryPayload, UpdateCategoryPayload } from '@/types'
import api from '@/services/api'

export const useCategoryStore = defineStore('categories', () => {
  const categories = shallowRef<Category[]>([])
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

  async function createCategory(payload: CreateCategoryPayload) {
    const { data } = await api.post('/api/v1/categories', payload)
    if (data.success) {
      categories.value = [data.data, ...categories.value]
    }
    return data
  }

  async function updateCategory(categoryId: string, payload: UpdateCategoryPayload) {
    const { data } = await api.put(`/api/v1/categories/${categoryId}`, payload)
    if (data.success) {
      categories.value = categories.value.map((c) =>
        c.id === categoryId ? { ...c, name: data.data.name } : c
      )
    }
    return data
  }

  return {
    categories,
    loading,
    fetchCategories,
    createCategory,
    updateCategory,
  }
})
