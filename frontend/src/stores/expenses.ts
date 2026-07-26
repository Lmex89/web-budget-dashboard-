import { defineStore } from 'pinia'
import { shallowRef, ref } from 'vue'
import type { ExpenseListItem, MonthlySummary, CategoryDistribution, CreateExpensePayload, UpdateExpensePayload } from '@/types'
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
  const recentExpenses = shallowRef<ExpenseListItem[]>([])
  const monthlySummary = shallowRef<MonthlySummary | null>(null)
  const categoryDistribution = shallowRef<CategoryDistribution[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(25)
  const totalPages = ref(0)
  const filterCategoryIds = ref<string[]>([])
  const filterStartDate = ref('')
  const filterEndDate = ref('')

  async function fetchExpenses(params?: FetchExpensesParams) {
    const { data } = await api.get('/api/v1/expenses', { params })
    if (data.success) {
      expenses.value = data.data
      total.value = data.total || 0
      currentPage.value = data.page || 1
      totalPages.value = data.total_pages || 0
    }
  }

  async function fetchRecentExpenses(params?: FetchExpensesParams) {
    const { data } = await api.get('/api/v1/expenses', { params })
    if (data.success) {
      recentExpenses.value = data.data
    }
  }

  function clearFilterState() {
    filterCategoryIds.value = []
    filterStartDate.value = ''
    filterEndDate.value = ''
  }

  async function createExpense(payload: CreateExpensePayload) {
    const { data } = await api.post('/api/v1/expenses', payload)
    return data
  }

  async function updateExpense(id: string, payload: UpdateExpensePayload) {
    const { data } = await api.put(`/api/v1/expenses/${id}`, payload)
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
    recentExpenses,
    monthlySummary,
    categoryDistribution,
    total,
    currentPage,
    pageSize,
    totalPages,
    filterCategoryIds,
    filterStartDate,
    filterEndDate,
    fetchExpenses,
    fetchRecentExpenses,
    clearFilterState,
    createExpense,
    updateExpense,
    deleteExpense,
    fetchMonthlySummary,
    fetchCategoryDistribution,
  }
})
