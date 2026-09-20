<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useBudgetStore } from '@/stores/budgets'
import { useCategoryStore } from '@/stores/categories'
import type { BudgetStatus } from '@/types'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import FormField from '@/components/ui/FormField.vue'
import { formatCurrency, formatMonthName, clamp } from '@/utils/format'
import { presetForCategory, hasBudgetPreset } from '@/utils/budgetPresets'

const budgetStore = useBudgetStore()
const categoryStore = useCategoryStore()

const now = new Date()
const currentMonth = ref(now.getMonth() + 1)
const currentYear = ref(now.getFullYear())

const editing = ref(false)
const confirmDelete = ref(false)
const totalBudget = ref<number>(0)
const categoryAmounts = ref<Record<string, number>>({})
const error = ref<string | null>(null)

const filterMonths = Array.from({ length: 12 }, (_, i) => i + 1)
const filterYears = Array.from({ length: 5 }, (_, i) => now.getFullYear() - i)

const progress = computed(() => budgetStore.progress)
const hasBudget = computed(() => !!progress.value)

const monthLabel = computed(() => `${formatMonthName(currentMonth.value)} ${currentYear.value}`)

const statusLabels: Record<BudgetStatus, string> = {
  on_track: 'On track',
  warning: 'Near limit',
  over: 'Over budget',
}

const statusChip: Record<BudgetStatus, string> = {
  on_track: 'chip-sage',
  warning: 'chip-warn',
  over: 'chip-danger',
}

const statusBar: Record<BudgetStatus, string> = {
  on_track: 'bg-sage',
  warning: 'bg-warn',
  over: 'bg-danger',
}

function barWidth(percentage: number): string {
  return `${clamp(percentage, 0, 100)}%`
}

function resetForm() {
  const current = progress.value
  const amounts: Record<string, number> = {}
  categoryStore.categories.forEach((category) => {
    amounts[category.id] = current ? 0 : presetForCategory(category.name)
  })
  if (current) {
    current.categories.forEach((category) => {
      amounts[category.category_id] = category.budget_amount
    })
  }
  totalBudget.value = current ? current.total_budget : 0
  categoryAmounts.value = amounts
}

async function load() {
  error.value = null
  confirmDelete.value = false
  await Promise.all([
    categoryStore.fetchCategories(),
    budgetStore.fetchProgress(currentYear.value, currentMonth.value),
  ])
  editing.value = !budgetStore.progress
  resetForm()
}

onMounted(load)

watch([currentMonth, currentYear], () => {
  load()
})

function startEditing() {
  resetForm()
  editing.value = true
}

function cancelEditing() {
  error.value = null
  editing.value = false
  resetForm()
}

async function handleSave() {
  error.value = null
  const total = Number(totalBudget.value)
  if (!Number.isFinite(total) || total <= 0) {
    error.value = 'Enter a total budget greater than zero.'
    return
  }

  const categories = categoryStore.categories
    .map((category) => ({
      category_id: category.id,
      amount: Number(categoryAmounts.value[category.id] || 0),
    }))
    .filter((item) => item.amount > 0)

  const categoryTotal = categories.reduce((sum, item) => sum + item.amount, 0)
  if (categoryTotal > total) {
    error.value = `Category limits (${formatCurrency(categoryTotal)}) exceed the total budget (${formatCurrency(total)}).`
    return
  }

  try {
    await budgetStore.saveBudget(currentYear.value, currentMonth.value, {
      total_budget: total,
      categories,
    })
    editing.value = false
    confirmDelete.value = false
    resetForm()
  } catch {
    error.value = 'Failed to save budget. Please try again.'
  }
}

async function handleDelete() {
  const current = progress.value
  if (!current) return
  error.value = null
  try {
    await budgetStore.deleteBudget(current.budget_id, currentYear.value, currentMonth.value)
    confirmDelete.value = false
    editing.value = true
    resetForm()
  } catch {
    error.value = 'Failed to delete budget. Please try again.'
  }
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader
      title="Budget"
      subtitle="Set monthly limits per category and track spending against them."
    >
      <template #action>
        <div class="flex items-center gap-2">
          <select v-model="currentMonth" class="eb-select w-28">
            <option v-for="month in filterMonths" :key="month" :value="month">
              {{ formatMonthName(month) }}
            </option>
          </select>
          <select v-model="currentYear" class="eb-select w-24">
            <option v-for="year in filterYears" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
        </div>
      </template>
    </PageHeader>

    <div v-if="budgetStore.loading" class="text-sm text-muted animate-pulse">Loading budget…</div>

    <form
      v-else-if="editing"
      class="paper-card p-5 md:p-6 space-y-6 animate-fade-up"
      @submit.prevent="handleSave"
    >
      <div>
        <h2 class="section-title">{{ hasBudget ? 'Edit budget' : 'Set this month’s budget' }}</h2>
        <p class="text-sm text-muted mt-1">{{ monthLabel }}</p>
      </div>

      <FormField label="Total monthly budget" for-id="total-budget">
        <input
          id="total-budget"
          v-model.number="totalBudget"
          type="number"
          class="eb-input"
          min="0.01"
          step="0.01"
          required
        />
      </FormField>

      <div>
        <p class="eb-label mb-3">Category limits</p>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div v-for="category in categoryStore.categories" :key="category.id">
            <label :for="`budget-${category.id}`" class="flex items-center gap-2 text-sm font-medium mb-1.5">
              <span
                class="w-2.5 h-2.5 rounded-full shrink-0"
                :style="{ backgroundColor: category.color || '#c7c7cc' }"
              />
              <span class="truncate">{{ category.name }}</span>
              <span
                v-if="hasBudgetPreset(category.name)"
                class="chip chip-muted ml-auto shrink-0"
              >
                preset {{ formatCurrency(presetForCategory(category.name)) }}
              </span>
            </label>
            <input
              :id="`budget-${category.id}`"
              v-model.number="categoryAmounts[category.id]"
              type="number"
              class="eb-input"
              min="0"
              step="0.01"
              placeholder="0.00"
            />
          </div>
        </div>
        <p class="text-xs text-muted mt-3">
          Tip: give your “Ahorro” category a limit to treat savings as a fixed monthly expense.
        </p>
      </div>

      <p v-if="error" class="text-sm font-medium text-danger">{{ error }}</p>

      <div class="flex items-center gap-3">
        <button type="submit" class="eb-btn eb-btn-primary" :disabled="budgetStore.saving">
          {{ budgetStore.saving ? 'Saving…' : 'Save budget' }}
        </button>
        <button v-if="hasBudget" type="button" class="eb-btn eb-btn-ghost" @click="cancelEditing">
          Cancel
        </button>
      </div>
    </form>

    <template v-else-if="progress">
      <PaperCard class="p-5 md:p-6 animate-fade-up">
        <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <p class="eyebrow mb-1">{{ monthLabel }}</p>
            <h2 class="section-title">Monthly overview</h2>
          </div>
          <span class="chip self-start" :class="statusChip[progress.status]">
            {{ statusLabels[progress.status] }}
          </span>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Budget</p>
            <p class="font-display text-2xl font-semibold tabular-nums mt-0.5">
              {{ formatCurrency(progress.total_budget) }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Spent</p>
            <p class="font-display text-2xl font-semibold tabular-nums mt-0.5">
              {{ formatCurrency(progress.total_spent) }}
            </p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Remaining</p>
            <p
              class="font-display text-2xl font-semibold tabular-nums mt-0.5"
              :class="progress.remaining < 0 ? 'text-danger' : 'text-sage'"
            >
              {{ formatCurrency(progress.remaining) }}
            </p>
          </div>
        </div>

        <div class="progress-track mt-6">
          <div
            class="progress-fill"
            :class="statusBar[progress.status]"
            :style="{ width: barWidth(progress.percentage) }"
          />
        </div>
        <div class="flex items-center justify-between text-xs text-muted mt-2">
          <span>{{ progress.percentage.toFixed(1) }}% of budget used</span>
          <span v-if="progress.unbudgeted_spent > 0">
            {{ formatCurrency(progress.unbudgeted_spent) }} spent outside category limits
          </span>
        </div>

        <div class="flex items-center gap-3 mt-6">
          <button class="eb-btn eb-btn-ghost text-xs" @click="startEditing">Edit budget</button>
          <template v-if="confirmDelete">
            <button
              class="eb-btn eb-btn-danger text-xs"
              :disabled="budgetStore.deleting"
              @click="handleDelete"
            >
              {{ budgetStore.deleting ? 'Deleting…' : 'Confirm delete' }}
            </button>
            <button class="eb-btn eb-btn-ghost text-xs" @click="confirmDelete = false">Cancel</button>
          </template>
          <button v-else class="text-xs font-semibold uppercase tracking-wide text-danger" @click="confirmDelete = true">
            Delete budget
          </button>
        </div>
      </PaperCard>

      <PaperCard class="p-5 md:p-6 animate-fade-up animation-delay-100">
        <h2 class="section-title mb-4">Category limits</h2>

        <div v-if="!progress.categories.length" class="text-sm text-muted">
          No category limits set. Edit the budget to add them.
        </div>

        <div v-else class="space-y-5">
          <div v-for="category in progress.categories" :key="category.category_id">
            <div class="flex items-center justify-between gap-4">
              <div class="flex items-center gap-2 min-w-0">
                <span
                  class="w-2.5 h-2.5 rounded-full shrink-0"
                  :style="{ backgroundColor: category.color || '#c7c7cc' }"
                />
                <p class="font-medium truncate">{{ category.category_name }}</p>
              </div>
              <span class="chip shrink-0" :class="statusChip[category.status]">
                {{ statusLabels[category.status] }}
              </span>
            </div>

            <div class="progress-track mt-2">
              <div
                class="progress-fill"
                :class="statusBar[category.status]"
                :style="{ width: barWidth(category.percentage) }"
              />
            </div>

            <div class="flex items-center justify-between text-xs text-muted mt-1.5">
              <span class="tabular-nums">
                {{ formatCurrency(category.spent) }} of {{ formatCurrency(category.budget_amount) }}
              </span>
              <span
                class="tabular-nums font-medium"
                :class="category.remaining < 0 ? 'text-danger' : 'text-sage'"
              >
                {{ category.remaining < 0 ? 'Over by' : 'Left' }}
                {{ formatCurrency(Math.abs(category.remaining)) }}
              </span>
            </div>
          </div>
        </div>
      </PaperCard>

      <p v-if="error" class="text-sm font-medium text-danger">{{ error }}</p>
    </template>
  </div>
</template>
