<script setup lang="ts">
import { onMounted } from 'vue'
import { useExpenseStore } from '@/stores/expenses'
import { useCategoryStore } from '@/stores/categories'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import FormField from '@/components/ui/FormField.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { formatCurrency, formatDate } from '@/utils/format'
import { useForm } from '@/composables/useForm'
import type { CreateExpensePayload } from '@/types'

const expenseStore = useExpenseStore()
const categoryStore = useCategoryStore()

interface ExpenseForm {
  amount: number
  description: string
  date: string
  payment_method: string
  category_id: string
  is_installment: boolean
  total_installments: number | null
}

const initialForm: ExpenseForm = {
  amount: 0,
  description: '',
  date: new Date().toISOString().split('T')[0],
  payment_method: 'debit',
  category_id: '',
  is_installment: false,
  total_installments: null,
}

const { form, showForm, toggleForm, handleSubmit } = useForm<ExpenseForm>({
  initialValues: initialForm,
  onSubmit: async (values) => {
    const payload: CreateExpensePayload = {
      ...values,
      date: new Date(values.date).toISOString(),
    }
    await expenseStore.createExpense(payload)
    await expenseStore.fetchExpenses()
  },
})

onMounted(() => {
  expenseStore.fetchExpenses()
  categoryStore.fetchCategories()
})

async function handleDelete(id: string) {
  await expenseStore.deleteExpense(id)
  expenseStore.fetchExpenses()
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Expenses" subtitle="Track every family spend in one place.">
      <template #action>
        <button class="eb-btn" :class="showForm ? 'eb-btn-ghost' : 'eb-btn-primary'" @click="toggleForm">
          {{ showForm ? 'Cancel' : 'Add expense' }}
        </button>
      </template>
    </PageHeader>

    <form
      v-if="showForm"
      @submit.prevent="handleSubmit"
      class="paper-card p-5 md:p-6 space-y-5 animate-fade-up"
    >
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <FormField label="Amount" for-id="amount">
          <input
            id="amount"
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
          <input id="date" v-model="form.date" type="date" class="eb-input" required />
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
      </div>

      <div class="flex items-center gap-3 pt-1">
        <button type="submit" class="eb-btn eb-btn-primary">Save expense</button>
        <button type="button" class="eb-btn eb-btn-ghost" @click="showForm = false">Cancel</button>
      </div>
    </form>

    <!-- Mobile list -->
    <div v-if="expenseStore.expenses.length > 0" class="md:hidden space-y-3">
      <PaperCard
        v-for="expense in expenseStore.expenses"
        :key="expense.id"
        class="p-4 flex items-center justify-between gap-4 animate-fade-up"
      >
        <div class="min-w-0">
          <p class="text-sm font-medium truncate">
            {{ expense.description || expense.category_name }}
          </p>
          <p class="text-xs text-muted mt-0.5">
            {{ formatDate(expense.date) }} · {{ expense.payment_method }}
          </p>
        </div>
        <div class="text-right shrink-0">
          <p class="text-sm font-semibold tabular-nums">{{ formatCurrency(expense.amount) }}</p>
          <button
            class="text-xs text-danger hover:underline mt-1"
            @click="handleDelete(expense.id)"
          >
            Delete
          </button>
        </div>
      </PaperCard>
    </div>

    <!-- Desktop table -->
    <PaperCard v-if="expenseStore.expenses.length > 0" class="hidden md:block overflow-hidden animate-fade-up">
      <table class="table-editorial">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Category</th>
            <th class="text-right">Amount</th>
            <th>Paid by</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="expense in expenseStore.expenses" :key="expense.id">
            <td class="text-muted">{{ formatDate(expense.date) }}</td>
            <td class="font-medium">{{ expense.description || '-' }}</td>
            <td>{{ expense.category_name }}</td>
            <td class="text-right font-semibold tabular-nums">{{ formatCurrency(expense.amount) }}</td>
            <td class="text-muted">{{ expense.user_name }}</td>
            <td>
              <button class="text-xs font-semibold text-danger hover:underline" @click="handleDelete(expense.id)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </PaperCard>

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
