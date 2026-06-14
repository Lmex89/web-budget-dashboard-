import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ExpenseListItem, MonthlySummary, CategoryDistribution } from '@/types'
import api from '@/services/api'

export const useExpenseStore = defineStore('expenses', () => {
  const expenses = ref<ExpenseListItem[]>([])
  const monthlySummary = ref<MonthlySummary | null>(null)
  const categoryDistribution = ref<CategoryDistribution[]>([])

  async function fetchExpenses(params?: {
    page?: number
    page_size?: number
    category_id?: string
    start_date?: string
    end_date?: string
  }) {
    const { data } = await api.get('/api/v1/expenses', { params })
    if (data.success) {
      expenses.value = data.data
    }
  }

  async function createExpense(payload: any) {
    const { data } = await api.post('/api/v1/expenses', payload)
    return data
  }

  async function deleteExpense(id: string) {
    const { data } = await api.delete(`/api/v1/expenses/${id}`)
    return data
  }

  async function fetchMonthlySummary(year: number, month: number) {
    const { data } = await api.get('/api/v1/expenses/analytics/monthly-summary', {
      params: { year, month },
    })
    if (data.success) {
      monthlySummary.value = data.data
    }
  }

  async function fetchCategoryDistribution(year: number, month: number) {
    const { data } = await api.get('/api/v1/expenses/analytics/category-distribution', {
      params: { year, month },
    })
    if (data.success) {
      categoryDistribution.value = data.data
    }
  }

  return {
    expenses,
    monthlySummary,
    categoryDistribution,
    fetchExpenses,
    createExpense,
    deleteExpense,
    fetchMonthlySummary,
    fetchCategoryDistribution,
  }
})
