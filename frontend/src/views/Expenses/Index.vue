<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useExpenseStore } from '@/stores/expenses'
import { useCategoryStore } from '@/stores/categories'
import { useCreditCardStore } from '@/stores/creditCards'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import FormField from '@/components/ui/FormField.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import CategoryFilter from '@/components/expenses/CategoryFilter.vue'
import { formatCurrency, formatDate } from '@/utils/format'
import { useForm } from '@/composables/useForm'
import api from '@/services/api'
import type { CreateExpensePayload, UpdateExpensePayload, ExpenseListItem } from '@/types'

const expenseStore = useExpenseStore()
const categoryStore = useCategoryStore()
const creditCardStore = useCreditCardStore()
const route = useRoute()

const formRef = ref<HTMLFormElement | null>(null)
const amountInputRef = ref<HTMLInputElement | null>(null)

function parseQueryCategoryIds(value: unknown): string[] {
  if (Array.isArray(value)) {
    return value
      .flatMap((v) => (v ? String(v).split(',') : []))
      .map((id) => id.trim())
      .filter(Boolean)
  }
  if (typeof value === 'string' && value) {
    return value.split(',').map((id) => id.trim()).filter(Boolean)
  }
  return []
}

const queryCategoryIds = parseQueryCategoryIds(route.query.category_id)
const queryStartDate = typeof route.query.start_date === 'string' ? route.query.start_date : ''
const queryEndDate = typeof route.query.end_date === 'string' ? route.query.end_date : ''
const selectedCategoryIds = ref<string[]>(
  queryCategoryIds.length > 0 ? queryCategoryIds : [...expenseStore.filterCategoryIds]
)
const filterStartDate = ref(queryStartDate || expenseStore.filterStartDate || '')
const filterEndDate = ref(queryEndDate || expenseStore.filterEndDate || '')
const editingId = ref<string | null>(null)
const confirmingDeleteId = ref<string | null>(null)
const deletingId = ref<string | null>(null)

function openDatePicker(e: MouseEvent) {
  ;(e.target as HTMLInputElement).showPicker()
}

interface ExpenseForm {
  amount: number
  description: string
  date: string
  payment_method: string
  category_id: string
  credit_card_id: string
}

const initialForm: ExpenseForm = {
  amount: 0,
  description: '',
  date: (() => {
    const now = new Date()
    const y = now.getFullYear()
    const m = String(now.getMonth() + 1).padStart(2, '0')
    const d = String(now.getDate()).padStart(2, '0')
    return `${y}-${m}-${d}`
  })(),
  payment_method: 'debit',
  category_id: '',
  credit_card_id: '',
}

const { form, showForm, handleSubmit, errorMessage, resetForm } = useForm<ExpenseForm>({
  initialValues: initialForm,
  onSubmit: async (values) => {
    const isoDate = new Date(values.date + 'T00:00:00').toISOString()
    if (editingId.value) {
      const payload: UpdateExpensePayload = {
        ...values,
        credit_card_id: values.credit_card_id || null,
        date: isoDate,
      }
      await expenseStore.updateExpense(editingId.value, payload)
      editingId.value = null
    } else {
      const payload: CreateExpensePayload = {
        ...values,
        credit_card_id: values.credit_card_id || null,
        is_installment: false,
        total_installments: null,
        date: isoDate,
      }
      await expenseStore.createExpense(payload)
    }
    await fetchExpenses()
  },
})

function startEdit(expense: ExpenseListItem) {
  confirmingDeleteId.value = null
  editingId.value = expense.id
  form.value.amount = Number(expense.amount)
  form.value.description = expense.description || ''
  form.value.date = expense.date.split('T')[0]
  form.value.payment_method = expense.payment_method
  form.value.category_id = expense.category_id
  form.value.credit_card_id = expense.credit_card_id || ''
  showForm.value = true
  nextTick(() => {
    formRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    amountInputRef.value?.focus()
    amountInputRef.value?.select()
  })
}

function handleToggleForm() {
  if (showForm.value) {
    cancelForm()
  } else {
    editingId.value = null
    resetForm()
    showForm.value = true
    nextTick(() => {
      formRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      amountInputRef.value?.focus()
    })
  }
}

function cancelForm() {
  editingId.value = null
  resetForm()
  showForm.value = false
}

const showCreditCardField = computed(() => form.value.payment_method === 'credit')

const formTitle = computed(() => editingId.value ? 'Edit expense' : 'New expense')
const submitLabel = computed(() => editingId.value ? 'Update expense' : 'Save expense')

async function fetchExpenses(page?: number) {
  await expenseStore.fetchExpenses({
    page: page || expenseStore.currentPage,
    page_size: expenseStore.pageSize,
    category_id: selectedCategoryIds.value.join(',') || undefined,
    start_date: filterStartDate.value || undefined,
    end_date: filterEndDate.value || undefined,
  })
}

function applyFilters() {
  expenseStore.filterCategoryIds = [...selectedCategoryIds.value]
  expenseStore.filterStartDate = filterStartDate.value
  expenseStore.filterEndDate = filterEndDate.value
  fetchExpenses(1)
}

async function clearFilters() {
  selectedCategoryIds.value = []
  filterStartDate.value = ''
  filterEndDate.value = ''
  await fetchExpenses(1)
  expenseStore.clearFilterState()
}

function goToPage(page: number) {
  fetchExpenses(page)
}

const visiblePages = computed(() => {
  const tp = expenseStore.totalPages
  if (tp <= 7) return Array.from({ length: tp }, (_, i) => i + 1)
  const cp = expenseStore.currentPage
  const pages: (number | string)[] = [1]
  if (cp > 3) pages.push('...')
  for (let i = Math.max(2, cp - 1); i <= Math.min(tp - 1, cp + 1); i++) {
    pages.push(i)
  }
  if (cp < tp - 2) pages.push('...')
  pages.push(tp)
  return pages
})

const hasActiveFilters = computed(
  () => selectedCategoryIds.value.length > 0 || filterStartDate.value || filterEndDate.value
)

async function exportCSV() {
  const params: Record<string, string> = {}
  if (selectedCategoryIds.value.length > 0) params.category_id = selectedCategoryIds.value.join(',')
  if (filterStartDate.value) params.start_date = filterStartDate.value
  if (filterEndDate.value) params.end_date = filterEndDate.value
  const { data } = await api.get('/api/v1/expenses/export/csv', { params, responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'expenses.csv')
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

const hasQueryFilters = queryCategoryIds.length > 0 || queryStartDate || queryEndDate

onMounted(() => {
  if (hasQueryFilters) {
    applyFilters()
  } else {
    fetchExpenses()
  }
  categoryStore.fetchCategories()
  creditCardStore.fetchCreditCards()
})

function promptDelete(id: string) {
  confirmingDeleteId.value = id
}

function cancelDelete() {
  confirmingDeleteId.value = null
}

async function confirmDelete(id: string) {
  deletingId.value = id
  try {
    await expenseStore.deleteExpense(id)
    confirmingDeleteId.value = null
    await fetchExpenses()
  } finally {
    deletingId.value = null
  }
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Expenses" subtitle="Track every family spend in one place.">
      <template #action>
        <button class="eb-btn" :class="showForm ? 'eb-btn-ghost' : 'eb-btn-primary'" @click="handleToggleForm">
          {{ showForm ? 'Cancel' : 'Add expense' }}
        </button>
      </template>
    </PageHeader>

    <PaperCard class="p-4 space-y-4" :class="showForm ? 'hidden md:block' : ''">
      <CategoryFilter
        v-model:selectedIds="selectedCategoryIds"
        :categories="categoryStore.categories"
      />
      <div class="flex flex-wrap items-end gap-3">
        <div class="flex flex-col gap-1 min-w-0">
          <label for="filter-start-date" class="eb-label text-xs">From</label>
          <input id="filter-start-date" v-model="filterStartDate" type="date" class="eb-input w-full sm:w-40" @click="openDatePicker" />
        </div>
        <div class="flex flex-col gap-1 min-w-0">
          <label for="filter-end-date" class="eb-label text-xs">To</label>
          <input id="filter-end-date" v-model="filterEndDate" type="date" class="eb-input w-full sm:w-40" @click="openDatePicker" />
        </div>
        <button
          class="eb-btn eb-btn-primary text-sm"
          @click="applyFilters"
        >
          Apply
        </button>
        <button
          v-if="hasActiveFilters"
          class="eb-btn eb-btn-ghost text-sm"
          @click="clearFilters"
        >
          Clear
        </button>
        <button class="eb-btn eb-btn-ghost text-sm ml-auto" @click="exportCSV">
          Export CSV
        </button>
      </div>
    </PaperCard>

    <form
      v-if="showForm"
      ref="formRef"
      @submit.prevent="handleSubmit"
      class="paper-card p-5 md:p-6 space-y-5 animate-fade-up transition-all duration-200"
      :class="editingId ? 'ring-2 ring-accent/50 shadow-md' : ''"
    >
      <div class="flex items-center justify-between">
        <h3 class="section-title text-base">{{ formTitle }}</h3>
        <span v-if="editingId" class="chip chip-accent text-xs">Editing expense</span>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <FormField label="Amount" for-id="amount">
          <input
            id="amount"
            ref="amountInputRef"
            v-model.number="form.amount"
            type="number"
            step="0.01"
            min="0"
            class="eb-input"
            placeholder="0.00"
            required
          />
        </FormField>

        <FormField label="Date" for-id="date">
          <input id="date" v-model="form.date" type="date" class="eb-input" required @click="openDatePicker" />
        </FormField>

        <FormField label="Description" for-id="description" class="md:col-span-2">
          <input
            id="description"
            v-model="form.description"
            type="text"
            class="eb-input"
            placeholder="What was this for?"
          />
        </FormField>

        <FormField label="Payment method" for-id="payment_method">
          <select id="payment_method" v-model="form.payment_method" class="eb-select">
            <option value="cash">Cash</option>
            <option value="debit">Debit</option>
            <option value="credit">Credit Card</option>
          </select>
        </FormField>

        <FormField label="Category" for-id="category_id">
          <select id="category_id" v-model="form.category_id" class="eb-select" required>
            <option value="" disabled>Select a category</option>
            <option v-for="category in categoryStore.categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
        </FormField>

        <FormField v-if="showCreditCardField" label="Credit card" for-id="credit_card_id">
          <select id="credit_card_id" v-model="form.credit_card_id" class="eb-select">
            <option value="" disabled>Select a card</option>
            <option v-for="card in creditCardStore.creditCards" :key="card.id" :value="card.id">
              {{ card.name }}
            </option>
          </select>
        </FormField>
      </div>

      <p v-if="errorMessage" class="text-sm text-danger">{{ errorMessage }}</p>

      <div class="flex items-center gap-3 pt-1">
        <button type="submit" class="eb-btn eb-btn-primary">{{ submitLabel }}</button>
        <button type="button" class="eb-btn eb-btn-ghost" @click="cancelForm">Cancel</button>
      </div>
    </form>

    <div v-if="expenseStore.expenses.length > 0" class="md:hidden space-y-3">
      <PaperCard
        v-for="expense in expenseStore.expenses"
        :key="expense.id"
        class="p-4 flex items-center justify-between gap-4 animate-fade-up transition-all"
        :class="editingId === expense.id ? 'ring-2 ring-accent bg-accent-light/30 dark:bg-accent/10' : ''"
      >
        <div class="min-w-0">
          <div class="flex items-center gap-2 min-w-0">
            <p class="text-sm font-medium truncate">
              {{ expense.description || expense.category_name }}
            </p>
            <span v-if="editingId === expense.id" class="chip chip-accent text-[10px] py-0 px-1.5 shrink-0">Editing</span>
          </div>
          <p class="text-xs text-muted mt-0.5">
            {{ formatDate(expense.date) }} · {{ expense.payment_method }}
          </p>
        </div>
        <div class="text-right shrink-0">
          <p class="text-sm font-semibold tabular-nums">{{ formatCurrency(expense.amount) }}</p>
          <div class="flex items-center justify-end gap-2 mt-1">
            <template v-if="confirmingDeleteId === expense.id">
              <button
                class="text-xs font-semibold text-danger px-2 py-1 rounded-lg bg-danger-light hover:opacity-80"
                :disabled="deletingId === expense.id"
                @click="confirmDelete(expense.id)"
              >
                {{ deletingId === expense.id ? 'Deleting…' : 'Confirm' }}
              </button>
              <button
                class="text-xs text-muted px-2 py-1 rounded-lg hover:bg-paper-dark"
                :disabled="deletingId === expense.id"
                @click="cancelDelete"
              >
                Cancel
              </button>
            </template>
            <template v-else>
              <button
                class="text-xs font-semibold px-2 py-1 rounded-lg transition-colors"
                :class="editingId === expense.id ? 'bg-accent text-white font-bold' : 'text-accent hover:bg-accent-light'"
                @click="startEdit(expense)"
              >
                {{ editingId === expense.id ? 'Editing' : 'Edit' }}
              </button>
              <button
                class="text-xs text-danger px-2 py-1 rounded-lg hover:bg-danger-light"
                @click="promptDelete(expense.id)"
              >
                Delete
              </button>
            </template>
          </div>
        </div>
      </PaperCard>
    </div>

    <PaperCard v-if="expenseStore.expenses.length > 0" class="hidden md:block overflow-hidden animate-fade-up">
      <table class="table-editorial">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Category</th>
            <th class="text-right">Amount</th>
            <th>Paid by</th>
            <th class="text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="expense in expenseStore.expenses"
            :key="expense.id"
            class="transition-colors"
            :class="editingId === expense.id ? 'bg-accent-light/40 dark:bg-accent/15' : ''"
          >
            <td class="text-muted">{{ formatDate(expense.date) }}</td>
            <td class="font-medium">
              <div class="flex items-center gap-2">
                <span>{{ expense.description || '-' }}</span>
                <span v-if="editingId === expense.id" class="chip chip-accent text-[10px] py-0 px-1.5 shrink-0">Editing</span>
              </div>
            </td>
            <td>{{ expense.category_name }}</td>
            <td class="text-right font-semibold tabular-nums">{{ formatCurrency(expense.amount) }}</td>
            <td class="text-muted">{{ expense.user_name }}</td>
            <td class="text-right whitespace-nowrap">
              <template v-if="confirmingDeleteId === expense.id">
                <button
                  class="text-xs font-semibold text-danger hover:underline mr-3"
                  :disabled="deletingId === expense.id"
                  @click="confirmDelete(expense.id)"
                >
                  {{ deletingId === expense.id ? 'Deleting…' : 'Confirm' }}
                </button>
                <button
                  class="text-xs font-semibold text-muted hover:underline"
                  :disabled="deletingId === expense.id"
                  @click="cancelDelete"
                >
                  Cancel
                </button>
              </template>
              <template v-else>
                <button
                  class="text-xs font-semibold hover:underline mr-3"
                  :class="editingId === expense.id ? 'text-accent font-bold underline' : 'text-accent'"
                  @click="startEdit(expense)"
                >
                  {{ editingId === expense.id ? 'Editing…' : 'Edit' }}
                </button>
                <button class="text-xs font-semibold text-danger hover:underline" @click="promptDelete(expense.id)">
                  Delete
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </PaperCard>

    <nav v-if="expenseStore.totalPages > 1" class="flex items-center justify-center gap-1 animate-fade-up" aria-label="Pagination">
      <button
        class="eb-btn eb-btn-ghost text-sm px-2"
        :disabled="expenseStore.currentPage <= 1"
        @click="goToPage(expenseStore.currentPage - 1)"
      >
        Prev
      </button>
      <template v-for="p in visiblePages" :key="p">
        <span v-if="p === '...'" class="px-1 text-muted text-sm">...</span>
        <button
          v-else
          class="eb-btn text-sm px-3"
          :class="p === expenseStore.currentPage ? 'eb-btn-primary' : 'eb-btn-ghost'"
          @click="goToPage(p as number)"
        >
          {{ p }}
        </button>
      </template>
      <button
        class="eb-btn eb-btn-ghost text-sm px-2"
        :disabled="expenseStore.currentPage >= expenseStore.totalPages"
        @click="goToPage(expenseStore.currentPage + 1)"
      >
        Next
      </button>
    </nav>

    <EmptyState
      v-if="expenseStore.expenses.length === 0"
      title="No expenses yet"
      description="Create your first expense to start tracking."
    >
      <template #icon>💰</template>
      <template #action>
        <button class="eb-btn eb-btn-primary" @click="showForm = true">Add expense</button>
      </template>
    </EmptyState>
  </div>
</template>
