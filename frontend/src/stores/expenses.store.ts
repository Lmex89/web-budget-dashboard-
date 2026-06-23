import { defineStore } from 'pinia'
import { shallowRef, ref, computed } from 'vue'
import type { DashboardExpense, DashboardSummary, CategoryBarSegment } from '@/types'
import {
  fetchDashboardExpenses,
  fetchDashboardSummary,
  fetchCategorySegments,
} from '@/services/expenses.service'

const MAX_VISIBLE_SEGMENTS = 5

export const useDashboardExpensesStore = defineStore('dashboard-expenses', () => {
  const expenses = shallowRef<DashboardExpense[]>([])
  const summary = shallowRef<DashboardSummary | null>(null)
  const rawSegments = shallowRef<CategoryBarSegment[]>([])
  const loadingExpenses = ref(false)
  const loadingSummary = ref(false)
  const loadingSegments = ref(false)
  const error = ref<string | null>(null)

  const isLoading = computed(
    () => loadingExpenses.value || loadingSummary.value || loadingSegments.value
  )

  const categorySegments = computed(() => {
    const segments = [...rawSegments.value].sort((a, b) => b.amount - a.amount)
    const total = segments.reduce((sum, s) => sum + s.amount, 0)

    if (segments.length <= MAX_VISIBLE_SEGMENTS + 1) {
      return segments.map((s) => ({
        ...s,
        percentage: total > 0 ? (s.amount / total) * 100 : 0,
      }))
    }

    const visible = segments.slice(0, MAX_VISIBLE_SEGMENTS)
    const others = segments.slice(MAX_VISIBLE_SEGMENTS)
    const othersAmount = others.reduce((sum, s) => sum + s.amount, 0)
    const othersCount = others.length

    const grouped: CategoryBarSegment = {
      categoryId: 'others',
      categoryName: `Otros (${othersCount})`,
      amount: othersAmount,
      percentage: total > 0 ? (othersAmount / total) * 100 : 0,
      colorIndex: 4,
    }

    return [
      ...visible.map((s) => ({
        ...s,
        percentage: total > 0 ? (s.amount / total) * 100 : 0,
      })),
      grouped,
    ]
  })

  const topCategories = computed(() => {
    return [...rawSegments.value]
      .sort((a, b) => b.amount - a.amount)
      .slice(0, 4)
  })

  async function loadExpenses() {
    loadingExpenses.value = true
    error.value = null
    try {
      expenses.value = await fetchDashboardExpenses()
    } catch (e) {
      error.value = 'Failed to load expenses'
      throw e
    } finally {
      loadingExpenses.value = false
    }
  }

  async function loadSummary() {
    loadingSummary.value = true
    error.value = null
    try {
      summary.value = await fetchDashboardSummary()
    } catch (e) {
      error.value = 'Failed to load summary'
      throw e
    } finally {
      loadingSummary.value = false
    }
  }

  async function loadSegments() {
    loadingSegments.value = true
    error.value = null
    try {
      rawSegments.value = await fetchCategorySegments()
    } catch (e) {
      error.value = 'Failed to load category breakdown'
      throw e
    } finally {
      loadingSegments.value = false
    }
  }

  async function loadAll() {
    await Promise.all([loadSummary(), loadSegments(), loadExpenses()])
  }

  return {
    expenses,
    summary,
    categorySegments,
    loadingExpenses,
    loadingSummary,
    loadingSegments,
    error,
    isLoading,
    topCategories,
    loadExpenses,
    loadSummary,
    loadSegments,
    loadAll,
  }
})
