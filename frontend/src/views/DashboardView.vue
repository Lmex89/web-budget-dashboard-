<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useDashboardExpensesStore } from '@/stores/expenses.store'
import { useAuthStore } from '@/stores/auth'
import StatCard from '@/components/dashboard/StatCard.vue'
import CategoryStackedBar from '@/components/dashboard/CategoryStackedBar.vue'
import RecentExpensesCard from '@/components/dashboard/RecentExpensesCard.vue'
import TopCategoriesCard from '@/components/dashboard/TopCategoriesCard.vue'
import { useCurrency } from '@/composables/useCurrency'
import { formatMonthName } from '@/utils/format'

const expensesStore = useDashboardExpensesStore()
const authStore = useAuthStore()
const { formatCurrency } = useCurrency()

const currentMonth = ref(6)
const currentYear = ref(2026)
const selectedCategory = ref('')

const monthLabel = 'June 2026'

const filterMonths = Array.from({ length: 12 }, (_, i) => i + 1)
const filterYears = [2026, 2025, 2024, 2023, 2022]

onMounted(() => {
  expensesStore.loadAll()
})

watch([currentMonth, currentYear, selectedCategory], () => {
  expensesStore.loadAll()
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
            <option value="cat-1">Entretenimiento</option>
            <option value="cat-2">Tdc Vexi Ñuis</option>
            <option value="cat-3">TDC Banamex ORO</option>
            <option value="cat-4">TDC INVEX Luis</option>
            <option value="cat-5">Comida</option>
            <option value="cat-6">Tarjeta vexi alma</option>
            <option value="cat-7">Varios</option>
            <option value="cat-8">Mutualista</option>
            <option value="cat-9">Salud</option>
            <option value="cat-10">Coche</option>
            <option value="cat-11">Transporte</option>
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
          :value="expensesStore.summary ? formatCurrency(expensesStore.summary.totalExpenses) : '$0.00'"
          :caption="monthLabel"
          tone="accent"
        />
      </div>
      <div class="animation-delay-200">
        <StatCard
          label="Categories used"
          :value="String(expensesStore.summary?.categoriesUsedCount || 0)"
          caption="Active this month"
          tone="ink"
        />
      </div>
      <div class="animation-delay-300">
        <StatCard
          label="Family members"
          :value="String(expensesStore.summary?.familyMembersCount || 0)"
          caption="Sharing this budget"
          tone="sage"
        />
      </div>
    </div>

    <!-- Stacked bar: full width always -->
    <div class="animation-delay-200">
      <CategoryStackedBar
        :segments="expensesStore.categorySegments"
        :total-label="monthLabel"
        :loading="expensesStore.loadingSegments"
        :error="expensesStore.error"
      />
    </div>

    <!-- Bottom grid: single column on mobile, 2-col on sm+ -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
      <div class="animation-delay-300">
        <RecentExpensesCard
          :expenses="expensesStore.expenses"
          :loading="expensesStore.loadingExpenses"
          :error="expensesStore.error"
        />
      </div>
      <div class="animation-delay-400">
        <TopCategoriesCard
          :categories="expensesStore.topCategories"
          :loading="expensesStore.loadingSegments"
          :error="expensesStore.error"
        />
      </div>
    </div>
  </div>
</template>
