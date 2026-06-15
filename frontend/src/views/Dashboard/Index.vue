<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useExpenseStore } from '@/stores/expenses'
import { useCategoryStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import PageHeader from '@/components/ui/PageHeader.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { formatCurrency, formatMonthName, formatShortDate } from '@/utils/format'

const expenseStore = useExpenseStore()
const categoryStore = useCategoryStore()
const authStore = useAuthStore()

const currentMonth = ref(new Date().getMonth() + 1)
const currentYear = ref(new Date().getFullYear())
const selectedCategory = ref('')

const monthLabel = computed(
  () => `${formatMonthName(currentMonth.value)} ${currentYear.value}`
)

async function loadData() {
  const categoryId = selectedCategory.value || undefined
  await Promise.all([
    expenseStore.fetchMonthlySummary(currentYear.value, currentMonth.value, categoryId),
    expenseStore.fetchCategoryDistribution(currentYear.value, currentMonth.value, categoryId),
    expenseStore.fetchExpenses({ page_size: 5 }),
  ])
}

onMounted(() => {
  categoryStore.fetchCategories()
  loadData()
})
watch([currentMonth, currentYear, selectedCategory], loadData)
</script>

<template>
  <div class="space-y-8">
    <PageHeader
      title="Overview"
      :subtitle="`Welcome back, ${authStore.user?.full_name || 'friend'}`"
      eyebrow="Dashboard"
    >
      <template #action>
        <div class="flex items-center gap-2">
          <select v-model="selectedCategory" class="eb-select w-40">
            <option value="">All categories</option>
            <option
              v-for="cat in categoryStore.categories"
              :key="cat.id"
              :value="cat.id"
            >
              {{ cat.name }}
            </option>
          </select>
          <select v-model="currentMonth" class="eb-select w-28">
            <option v-for="m in 12" :key="m" :value="m">
              {{ formatMonthName(m) }}
            </option>
          </select>
          <select v-model="currentYear" class="eb-select w-24">
            <option v-for="y in 5" :key="y" :value="currentYear - y + 1">
              {{ currentYear - y + 1 }}
            </option>
          </select>
        </div>
      </template>
    </PageHeader>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-5">
      <MetricCard
        label="Total expenses"
        :value="formatCurrency(expenseStore.monthlySummary?.total_expenses)"
        :caption="monthLabel"
        tone="accent"
        class="animation-delay-100"
      />
      <MetricCard
        label="Categories used"
        :value="String(expenseStore.categoryDistribution?.length || 0)"
        caption="Active this month"
        tone="ink"
        class="animation-delay-200"
      />
      <MetricCard
        label="Family members"
        value="1"
        caption="Sharing this budget"
        tone="sage"
        class="animation-delay-300"
      />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Category distribution -->
      <PaperCard class="p-5 md:p-6 animate-fade-up animation-delay-300">
        <h2 class="section-title mb-6">Category distribution</h2>
        <div v-if="expenseStore.categoryDistribution && expenseStore.categoryDistribution.length > 0" class="space-y-4">
          <div
            v-for="cat in expenseStore.categoryDistribution"
            :key="cat.category"
            class="flex items-center gap-4"
          >
            <div
              class="w-3 h-3 rounded-full shrink-0"
              :style="{ backgroundColor: cat.color || '#a8a29e' }"
            />
            <div class="flex-1 min-w-0">
              <div class="flex items-baseline justify-between gap-2">
                <span class="text-sm font-medium truncate">{{ cat.category }}</span>
                <span class="text-sm font-semibold tabular-nums">
                  {{ formatCurrency(cat.amount) }}
                </span>
              </div>
              <div class="progress-track mt-2">
                <div
                  class="progress-fill bg-accent"
                  :style="{
                    width:
                      expenseStore.monthlySummary?.total_expenses && Number(expenseStore.monthlySummary.total_expenses) > 0
                        ? `${(cat.amount / Number(expenseStore.monthlySummary.total_expenses)) * 100}%`
                        : '0%',
                  }"
                />
              </div>
            </div>
          </div>
        </div>
        <div v-else class="pt-4">
          <EmptyState
            title="No expenses yet"
            description="Add your first expense to see the monthly breakdown."
          >
            <template #icon>📊</template>
            <template #action>
              <router-link to="/expenses" class="eb-btn eb-btn-primary"> Add expense </router-link>
            </template>
          </EmptyState>
        </div>
      </PaperCard>

      <!-- Recent expenses -->
      <PaperCard class="p-5 md:p-6 animate-fade-up animation-delay-400">
        <div class="flex items-baseline justify-between mb-6">
          <h2 class="section-title">Recent expenses</h2>
          <router-link to="/expenses" class="text-xs font-semibold text-accent hover:underline">
            View all
          </router-link>
        </div>

        <div v-if="expenseStore.expenses.length > 0" class="divide-y divide-rule">
          <div
            v-for="expense in expenseStore.expenses"
            :key="expense.id"
            class="flex items-center justify-between py-3.5 gap-4"
          >
            <div class="min-w-0">
              <p class="text-sm font-medium truncate">
                {{ expense.description || expense.category_name }}
              </p>
              <p class="text-xs text-muted mt-0.5">
                {{ expense.user_name }} · {{ formatShortDate(expense.date) }}
              </p>
            </div>
            <span class="text-sm font-semibold tabular-nums text-ink">
              {{ formatCurrency(expense.amount) }}
            </span>
          </div>
        </div>

        <EmptyState
          v-else
          title="Nothing here"
          description="Track a new expense and it will appear here."
        >
          <template #icon>💰</template>
          <template #action>
            <router-link to="/expenses" class="eb-btn eb-btn-ghost">Add one</router-link>
          </template>
        </EmptyState>
      </PaperCard>
    </div>
  </div>
</template>
