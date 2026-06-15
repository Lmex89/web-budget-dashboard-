import { defineStore } from 'pinia'
import { shallowRef } from 'vue'
import type { ExpenseListItem, MonthlySummary, CategoryDistribution, CreateExpensePayload } from '@/types'
import api from '@/services/api'

interface FetchExpensesParams {
  page?: number
  page_size?: number
  category_id?: string
  start_date?: string
  end_date?: string
}

export const useExpenseStore = defineStore('expenses', () => {
  const expenses = shallowRef<ExpenseListItem[]>([])
  const monthlySummary = shallowRef<MonthlySummary | null>(null)
  const categoryDistribution = shallowRef<CategoryDistribution[]>([])

  async function fetchExpenses(params?: FetchExpensesParams) {
    const { data } = await api.get('/api/v1/expenses', { params })
    if (data.success) {
      expenses.value = data.data
    }
  }

  async function createExpense(payload: CreateExpensePayload) {
    const { data } = await api.post('/api/v1/expenses', payload)
    return data
  }

  async function deleteExpense(id: string) {
    const { data } = await api.delete(`/api/v1/expenses/${id}`)
    return data
  }

  async function fetchMonthlySummary(year: number, month: number, category_id?: string) {
    const params: Record<string, string | number> = { year, month }
    if (category_id) params.category_id = category_id
    const { data } = await api.get('/api/v1/expenses/analytics/monthly-summary', { params })
    if (data.success) {
      monthlySummary.value = data.data
    }
  }

  async function fetchCategoryDistribution(year: number, month: number, category_id?: string) {
    const params: Record<string, string | number> = { year, month }
    if (category_id) params.category_id = category_id
    const { data } = await api.get('/api/v1/expenses/analytics/category-distribution', { params })
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
