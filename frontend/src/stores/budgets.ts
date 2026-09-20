import { defineStore } from 'pinia'
import { shallowRef, ref } from 'vue'
import type { Budget, BudgetProgress, BudgetUpsertPayload } from '@/types'
import api from '@/services/api'

export const useBudgetStore = defineStore('budgets', () => {
  const progress = shallowRef<BudgetProgress | null>(null)
  const budgets = shallowRef<Budget[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const deleting = ref(false)

  async function fetchProgress(year: number, month: number) {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/budgets/progress', { params: { year, month } })
      if (data.success) {
        progress.value = data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchBudgets(year?: number) {
    const params = year ? { year } : undefined
    const { data } = await api.get('/api/v1/budgets', { params })
    if (data.success) {
      budgets.value = data.data
    }
  }

  async function saveBudget(year: number, month: number, payload: BudgetUpsertPayload) {
    saving.value = true
    try {
      const { data } = await api.put(`/api/v1/budgets/${year}/${month}`, payload)
      if (data.success) {
        await fetchProgress(year, month)
      }
      return data
    } finally {
      saving.value = false
    }
  }

  async function deleteBudget(budgetId: string, year: number, month: number) {
    deleting.value = true
    try {
      const { data } = await api.delete(`/api/v1/budgets/${budgetId}`)
      if (data.success) {
        await fetchProgress(year, month)
      }
      return data
    } finally {
      deleting.value = false
    }
  }

  function clearProgress() {
    progress.value = null
  }

  return {
    progress,
    budgets,
    loading,
    saving,
    deleting,
    fetchProgress,
    fetchBudgets,
    saveBudget,
    deleteBudget,
    clearProgress,
  }
})
