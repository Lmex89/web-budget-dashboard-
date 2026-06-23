<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useExpenseStore } from '@/stores/expenses'
import { useCategoryStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import StatCard from '@/components/dashboard/StatCard.vue'
import CategoryStackedBar from '@/components/dashboard/CategoryStackedBar.vue'
import RecentExpensesCard from '@/components/dashboard/RecentExpensesCard.vue'
import TopCategoriesCard from '@/components/dashboard/TopCategoriesCard.vue'
import { useCurrency } from '@/composables/useCurrency'
import { formatMonthName } from '@/utils/format'
import type { CategoryBarSegment, DashboardExpense, DashboardSummary } from '@/types'

const expenseStore = useExpenseStore()
const categoryStore = useCategoryStore()
const authStore = useAuthStore()
const { formatCurrency } = useCurrency()

const now = new Date()
const currentMonth = ref(now.getMonth() + 1)
const currentYear = ref(now.getFullYear())
const selectedCategory = ref('')

const loadingExpenses = ref(false)
const loadingSegments = ref(false)
const error = ref<string | null>(null)

const monthLabel = computed(() => {
  const d = new Date(currentYear.value, currentMonth.value - 1)
  return d.toLocaleString('en-US', { month: 'long', year: 'numeric' })
})

const filterMonths = Array.from({ length: 12 }, (_, i) => i + 1)
const filterYears = Array.from({ length: 5 }, (_, i) => now.getFullYear() - i)

const categories = computed(() => categoryStore.categories)

const summary = computed<DashboardSummary | null>(() => {
  const ms = expenseStore.monthlySummary
  if (!ms) return null
  return {
    totalExpenses: ms.total_expenses,
    categoriesUsedCount: expenseStore.categoryDistribution.length,
    familyMembersCount: 0,
    month: ms.month,
    year: ms.year,
  }
})

const MAX_VISIBLE_SEGMENTS = 5

const categorySegments = computed<CategoryBarSegment[]>(() => {
  const dist = expenseStore.categoryDistribution
  const catMap = new Map(categoryStore.categories.map((c) => [c.name.toLowerCase(), c]))
  const segments: CategoryBarSegment[] = dist.map((d) => {
    const cat = catMap.get(d.category.toLowerCase())
    return { categoryId: cat?.id || d.category, categoryName: d.category, amount: d.amount, percentage: 0, color: d.color }
  })
  segments.sort((a, b) => b.amount - a.amount)
  const total = segments.reduce((sum, s) => sum + s.amount, 0)
  if (segments.length <= MAX_VISIBLE_SEGMENTS + 1) {
    return segments.map((s) => ({ ...s, percentage: total > 0 ? (s.amount / total) * 100 : 0 }))
  }
  const visible = segments.slice(0, MAX_VISIBLE_SEGMENTS)
  const others = segments.slice(MAX_VISIBLE_SEGMENTS)
  const othersAmount = others.reduce((sum, s) => sum + s.amount, 0)
  return [
    ...visible.map((s) => ({ ...s, percentage: total > 0 ? (s.amount / total) * 100 : 0 })),
    { categoryId: 'others', categoryName: `Otros (${others.length})`, amount: othersAmount, percentage: total > 0 ? (othersAmount / total) * 100 : 0, color: null },
  ]
})

const topCategories = computed<CategoryBarSegment[]>(() => categorySegments.value.slice(0, 6))

const recentExpenses = computed<DashboardExpense[]>(() =>
  expenseStore.expenses.map((e) => ({
    id: e.id,
    description: e.description || '',
    amount: typeof e.amount === 'string' ? parseFloat(e.amount) : e.amount,
    date: e.date,
    categoryId: '',
    authorName: e.user_name,
  }))
)

function monthDateRange(year: number, month: number) {
  const start = `${year}-${String(month).padStart(2, '0')}-01`
  const lastDay = new Date(year, month, 0).getDate()
  const end = `${year}-${String(month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
  return { start, end }
}

async function loadAll() {
  loadingSegments.value = true
  loadingExpenses.value = true
  error.value = null
  const catId = selectedCategory.value || undefined
  const { start, end } = monthDateRange(currentYear.value, currentMonth.value)
  try {
    await Promise.all([
      expenseStore.fetchMonthlySummary(currentYear.value, currentMonth.value, catId),
      expenseStore.fetchCategoryDistribution(currentYear.value, currentMonth.value, catId),
      expenseStore.fetchExpenses({ page: 1, page_size: 5, start_date: start, end_date: end, category_id: catId }),
    ])
  } catch {
    error.value = 'Failed to load dashboard data'
  } finally {
    loadingSegments.value = false
    loadingExpenses.value = false
  }
}

onMounted(async () => {
  await Promise.all([categoryStore.fetchCategories(), loadAll()])
})

watch([currentMonth, currentYear, selectedCategory], () => {
  loadAll()
})
</script>

<template>
  <div class="space-y-5 sm:space-y-6 lg:space-y-8">
    <!-- Header: stacked on mobile, flex row on lg+ -->
    <div class="animate-fade-up">
      <p class="eyebrow mb-2">Dashboard</p>
      <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
        <div>
          <h1 class="page-title">Overview</h1>
          <p class="page-subtitle mt-2 max-w-md">
            Welcome back, {{ authStore.user?.full_name || 'friend' }}
          </p>
        </div>

        <!-- Filters: horizontally scrollable on mobile, inline on lg -->
        <div class="flex items-center gap-2 overflow-x-auto -mx-1 px-1 pb-1 lg:overflow-visible lg:mx-0 lg:px-0 lg:pb-0 shrink-0">
          <select v-model="selectedCategory" class="eb-select flex-1 min-w-[130px] lg:flex-none lg:w-40">
            <option value="">All categories</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <select v-model="currentMonth" class="eb-select flex-1 min-w-[100px] lg:flex-none lg:w-28">
            <option v-for="m in filterMonths" :key="m" :value="m">
              {{ formatMonthName(m) }}
            </option>
          </select>
          <select v-model="currentYear" class="eb-select flex-1 min-w-[80px] lg:flex-none lg:w-24">
            <option v-for="y in filterYears" :key="y" :value="y">
              {{ y }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Stat cards: single-column rows on mobile, 3-col on sm+ -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 md:gap-5">
      <div class="animation-delay-100">
        <StatCard
          label="Total expenses"
          :value="summary ? formatCurrency(summary.totalExpenses) : '$0.00'"
          :caption="monthLabel"
          tone="accent"
        />
      </div>
      <div class="animation-delay-200">
        <StatCard
          label="Categories used"
           :value="String(summary?.categoriesUsedCount || 0)"
          caption="Active this month"
          tone="ink"
        />
      </div>
      <div class="animation-delay-300">
        <StatCard
          label="Family members"
           :value="String(summary?.familyMembersCount || 0)"
          caption="Sharing this budget"
          tone="sage"
        />
      </div>
    </div>

    <!-- Stacked bar: full width always -->
    <div class="animation-delay-200">
      <CategoryStackedBar
        :segments="categorySegments"
        :total-label="monthLabel"
        :loading="loadingSegments"
        :error="error"
      />
    </div>

    <!-- Bottom grid: single column on mobile, 2-col on sm+ -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
      <div class="animation-delay-300">
        <RecentExpensesCard
          :expenses="recentExpenses"
          :loading="loadingExpenses"
          :error="error"
        />
      </div>
      <div class="animation-delay-400">
        <TopCategoriesCard
          :categories="topCategories"
          :loading="loadingSegments"
          :error="error"
        />
      </div>
    </div>
  </div>
</template>
