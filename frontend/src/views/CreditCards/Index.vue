<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { CreditCard } from '@/types'
import { useCreditCardStore } from '@/stores/creditCards'

const creditCardStore = useCreditCardStore()
const showForm = ref(false)
const errorMessage = ref('')
const submitting = ref(false)

const form = ref({
  name: '',
  last_four_digits: '',
  limit: 0,
  closing_day: 1,
  due_day: 1,
  current_balance: 0,
})

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

onMounted(async () => {
  await creditCardStore.fetchCreditCards()
})

function toNumber(value: string | number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function formatCurrency(value: string | number): string {
  return currencyFormatter.format(toNumber(value))
}

function utilization(card: CreditCard): number {
  const limit = toNumber(card.limit)
  if (limit <= 0) {
    return 0
  }
  const balance = toNumber(card.current_balance)
  const ratio = (balance / limit) * 100
  return Math.max(0, Math.min(100, Math.round(ratio)))
}

function resetForm() {
  form.value = {
    name: '',
    last_four_digits: '',
    limit: 0,
    closing_day: 1,
    due_day: 1,
    current_balance: 0,
  }
}

async function handleCreate() {
  errorMessage.value = ''
  submitting.value = true

  try {
    await creditCardStore.createCreditCard({
      name: form.value.name.trim(),
      last_four_digits: form.value.last_four_digits.trim() || null,
      limit: Number(form.value.limit),
      closing_day: Number(form.value.closing_day),
      due_day: Number(form.value.due_day),
      current_balance: Number(form.value.current_balance),
    })
    showForm.value = false
    resetForm()
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.error?.message || 'Failed to create credit card'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Credit cards</h1>
        <p class="text-base-content/60 text-sm">Track limits, balances, and due dates</p>
      </div>
      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Add card' }}
      </button>
    </div>

    <form v-if="showForm" class="card bg-base-100 shadow-sm p-6 space-y-4" @submit.prevent="handleCreate">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="form-control">
          <label class="label"><span class="label-text">Card name</span></label>
          <input v-model="form.name" type="text" class="input input-bordered" maxlength="100" required />
        </div>
        <div class="form-control">
          <label class="label"><span class="label-text">Last 4 digits (optional)</span></label>
          <input
            v-model="form.last_four_digits"
            type="text"
            class="input input-bordered"
            maxlength="4"
            pattern="[0-9]{4}"
            placeholder="1234"
          />
        </div>

        <div class="form-control">
          <label class="label"><span class="label-text">Card limit</span></label>
          <input v-model.number="form.limit" type="number" class="input input-bordered" min="0.01" step="0.01" required />
        </div>
        <div class="form-control">
          <label class="label"><span class="label-text">Current balance</span></label>
          <input v-model.number="form.current_balance" type="number" class="input input-bordered" min="0" step="0.01" />
        </div>

        <div class="form-control">
          <label class="label"><span class="label-text">Closing day</span></label>
          <input v-model.number="form.closing_day" type="number" class="input input-bordered" min="1" max="31" required />
        </div>
        <div class="form-control">
          <label class="label"><span class="label-text">Due day</span></label>
          <input v-model.number="form.due_day" type="number" class="input input-bordered" min="1" max="31" required />
        </div>
      </div>

      <p v-if="errorMessage" class="text-error text-sm">{{ errorMessage }}</p>

      <button type="submit" class="btn btn-primary w-fit" :disabled="submitting">
        {{ submitting ? 'Saving...' : 'Save credit card' }}
      </button>
    </form>

    <div v-if="creditCardStore.loading" class="text-base-content/60">Loading credit cards...</div>

    <div v-else-if="creditCardStore.creditCards.length === 0" class="card bg-base-100 shadow-sm p-10 text-center text-base-content/60">
      No credit cards found. Add your first one.
    </div>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div v-for="card in creditCardStore.creditCards" :key="card.id" class="card bg-base-100 shadow-sm">
        <div class="card-body">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="card-title text-lg">{{ card.name }}</h2>
              <p class="text-sm text-base-content/50">•••• {{ card.last_four_digits || '----' }}</p>
            </div>
            <div class="badge badge-outline">{{ utilization(card) }}% used</div>
          </div>
          <div class="mt-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Limit</span>
              <span class="font-semibold">{{ formatCurrency(card.limit) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Balance</span>
              <span class="font-semibold">{{ formatCurrency(card.current_balance) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Closing day</span>
              <span>{{ card.closing_day }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Due day</span>
              <span>{{ card.due_day }}</span>
            </div>
          </div>
          <div class="w-full bg-base-200 rounded-full h-2 mt-3">
            <div class="bg-primary h-2 rounded-full transition-all" :style="{ width: utilization(card) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
