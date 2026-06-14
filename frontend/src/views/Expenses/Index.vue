<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useExpenseStore } from '@/stores/expenses'

const expenseStore = useExpenseStore()
const showForm = ref(false)

const form = ref({
  amount: 0,
  description: '',
  date: new Date().toISOString().split('T')[0],
  payment_method: 'debit',
  category_id: '',
  is_installment: false,
  total_installments: null as number | null,
})

onMounted(() => {
  expenseStore.fetchExpenses()
})

async function handleCreate() {
  await expenseStore.createExpense({
    ...form.value,
    date: new Date(form.value.date).toISOString(),
  })
  showForm.value = false
  resetForm()
  expenseStore.fetchExpenses()
}

function resetForm() {
  form.value = {
    amount: 0,
    description: '',
    date: new Date().toISOString().split('T')[0],
    payment_method: 'debit',
    category_id: '',
    is_installment: false,
    total_installments: null,
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Expenses</h1>
        <p class="text-base-content/60 text-sm">Manage your family expenses</p>
      </div>
      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Add expense' }}
      </button>
    </div>

    <form v-if="showForm" @submit.prevent="handleCreate" class="card bg-base-100 shadow-sm p-6 space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="form-control">
          <label class="label"><span class="label-text">Amount</span></label>
          <input v-model.number="form.amount" type="number" step="0.01" min="0" class="input input-bordered" required />
        </div>
        <div class="form-control">
          <label class="label"><span class="label-text">Date</span></label>
          <input v-model="form.date" type="date" class="input input-bordered" required />
        </div>
        <div class="form-control md:col-span-2">
          <label class="label"><span class="label-text">Description</span></label>
          <input v-model="form.description" type="text" class="input input-bordered" />
        </div>
        <div class="form-control">
          <label class="label"><span class="label-text">Payment method</span></label>
          <select v-model="form.payment_method" class="select select-bordered">
            <option value="cash">Cash</option>
            <option value="debit">Debit</option>
            <option value="credit">Credit Card</option>
          </select>
        </div>
        <div class="form-control">
          <label class="label"><span class="label-text">Category</span></label>
          <select v-model="form.category_id" class="select select-bordered" required>
            <option value="" disabled>Select category</option>
          </select>
        </div>
      </div>
      <button type="submit" class="btn btn-primary">Save expense</button>
    </form>

    <div class="overflow-x-auto">
      <table class="table table-zebra">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Category</th>
            <th>Amount</th>
            <th>Paid by</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="expense in expenseStore.expenses" :key="expense.id">
            <td>{{ new Date(expense.date).toLocaleDateString() }}</td>
            <td>{{ expense.description || '-' }}</td>
            <td>{{ expense.category_name }}</td>
            <td class="font-semibold">${{ parseFloat(expense.amount).toFixed(2) }}</td>
            <td>{{ expense.user_name }}</td>
            <td>
              <button class="btn btn-ghost btn-xs" @click="expenseStore.deleteExpense(expense.id); expenseStore.fetchExpenses()">Delete</button>
            </td>
          </tr>
          <tr v-if="expenseStore.expenses.length === 0">
            <td colspan="6" class="text-center text-base-content/40 py-8">No expenses found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
