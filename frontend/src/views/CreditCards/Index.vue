<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { CreditCard } from '@/types'
import { useCreditCardStore } from '@/stores/creditCards'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import FormField from '@/components/ui/FormField.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { formatCurrency, formatDate, clamp } from '@/utils/format'
import { useForm } from '@/composables/useForm'

const creditCardStore = useCreditCardStore()

const UTILIZATION_HIGH = 80
const UTILIZATION_MEDIUM = 50

const expandedCard = ref<string | null>(null)

interface CreditCardForm {
  name: string
  last_four_digits: string
  limit: number
  closing_day: number
  due_day: number
  current_balance: number
}

const initialForm: CreditCardForm = {
  name: '',
  last_four_digits: '',
  limit: 0,
  closing_day: 1,
  due_day: 1,
  current_balance: 0,
}

const { form, showForm, errorMessage, isSubmitting, toggleForm, handleSubmit } = useForm<CreditCardForm>({
  initialValues: initialForm,
  onSubmit: async (values) => {
    await creditCardStore.createCreditCard({
      name: values.name.trim(),
      last_four_digits: values.last_four_digits.trim() || null,
      limit: Number(values.limit),
      closing_day: Number(values.closing_day),
      due_day: Number(values.due_day),
      current_balance: Number(values.current_balance),
    })
  },
})

onMounted(async () => {
  await creditCardStore.fetchCreditCards()
})

function toNumber(value: string | number): number {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : 0
}

function utilization(card: CreditCard): number {
  const limit = toNumber(card.limit)
  if (limit <= 0) return 0
  const ratio = (toNumber(card.current_balance) / limit) * 100
  return clamp(Math.round(ratio), 0, 100)
}

function getUtilizationTone(value: number): string {
  if (value > UTILIZATION_HIGH) return 'chip-danger'
  if (value > UTILIZATION_MEDIUM) return 'chip-warn'
  return 'chip-sage'
}

function getUtilizationBarTone(value: number): string {
  if (value > UTILIZATION_HIGH) return 'bg-danger'
  if (value > UTILIZATION_MEDIUM) return 'bg-warn'
  return 'bg-sage'
}

async function toggleExpenses(cardId: string) {
  if (expandedCard.value === cardId) {
    expandedCard.value = null
    return
  }
  expandedCard.value = cardId
  if (!creditCardStore.getExpenses(cardId).length) {
    await creditCardStore.fetchCardExpenses(cardId)
  }
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Credit cards" subtitle="Limits, balances, and due dates at a glance.">
      <template #action>
        <button class="eb-btn" :class="showForm ? 'eb-btn-ghost' : 'eb-btn-primary'" @click="toggleForm">
          {{ showForm ? 'Cancel' : 'Add card' }}
        </button>
      </template>
    </PageHeader>

    <form
      v-if="showForm"
      class="paper-card p-5 md:p-6 space-y-5 animate-fade-up"
      @submit.prevent="handleSubmit"
    >
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <FormField label="Card name" for-id="card-name">
          <input
            id="card-name"
            v-model="form.name"
            type="text"
            class="eb-input"
            maxlength="100"
            placeholder="e.g. Platinum Card"
            required
          />
        </FormField>

        <FormField label="Last 4 digits" for-id="card-digits">
          <input
            id="card-digits"
            v-model="form.last_four_digits"
            type="text"
            class="eb-input"
            maxlength="4"
            pattern="[0-9]{4}"
            placeholder="1234"
          />
        </FormField>

        <FormField label="Card limit" for-id="card-limit">
          <input
            id="card-limit"
            v-model.number="form.limit"
            type="number"
            class="eb-input"
            min="0.01"
            step="0.01"
            required
          />
        </FormField>

        <FormField label="Current balance" for-id="card-balance">
          <input
            id="card-balance"
            v-model.number="form.current_balance"
            type="number"
            class="eb-input"
            min="0"
            step="0.01"
          />
        </FormField>

        <FormField label="Closing day" for-id="closing-day">
          <input
            id="closing-day"
            v-model.number="form.closing_day"
            type="number"
            class="eb-input"
            min="1"
            max="31"
            required
          />
        </FormField>

        <FormField label="Due day" for-id="due-day">
          <input
            id="due-day"
            v-model.number="form.due_day"
            type="number"
            class="eb-input"
            min="1"
            max="31"
            required
          />
        </FormField>
      </div>

      <p v-if="errorMessage" class="text-sm font-medium text-danger">{{ errorMessage }}</p>

      <div class="flex items-center gap-3">
        <button type="submit" class="eb-btn eb-btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving…' : 'Save credit card' }}
        </button>
        <button type="button" class="eb-btn eb-btn-ghost" @click="showForm = false">Cancel</button>
      </div>
    </form>

    <div v-if="creditCardStore.loading" class="text-sm text-muted animate-pulse">Loading cards…</div>

    <EmptyState
      v-else-if="creditCardStore.creditCards.length === 0"
      title="No cards on file"
      description="Add a credit card to track utilization."
    >
      <template #icon>💳</template>
      <template #action>
        <button class="eb-btn eb-btn-primary" @click="showForm = true">Add card</button>
      </template>
    </EmptyState>

    <div v-else class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <PaperCard
        v-for="card in creditCardStore.creditCards"
        :key="card.id"
        class="p-5 animate-fade-up"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <h3 class="font-display text-xl tracking-tight">{{ card.name }}</h3>
            <p class="text-sm text-muted mt-0.5">•••• {{ card.last_four_digits || '----' }}</p>
          </div>
          <span class="chip" :class="getUtilizationTone(utilization(card))">
            {{ utilization(card) }}% used
          </span>
        </div>

        <div class="grid grid-cols-2 gap-y-4 gap-x-6 mt-6 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Limit</p>
            <p class="font-semibold tabular-nums mt-0.5">{{ formatCurrency(card.limit) }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Balance</p>
            <p class="font-semibold tabular-nums mt-0.5">{{ formatCurrency(card.current_balance) }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Closing day</p>
            <p class="font-medium mt-0.5">{{ card.closing_day }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Due day</p>
            <p class="font-medium mt-0.5">{{ card.due_day }}</p>
          </div>
        </div>

        <div class="progress-track mt-5">
          <div
            class="progress-fill"
            :class="getUtilizationBarTone(utilization(card))"
            :style="{ width: utilization(card) + '%' }"
          />
        </div>

        <button
          class="mt-4 text-xs font-semibold uppercase tracking-wide text-accent hover:text-accent-dark"
          @click="toggleExpenses(card.id)"
        >
          {{ expandedCard === card.id ? 'Hide expenses' : 'Show expenses' }}
          ({{ creditCardStore.getExpenses(card.id).length }})
        </button>

        <div v-if="expandedCard === card.id" class="mt-3 space-y-2 animate-fade-up">
          <div
            v-for="expense in creditCardStore.getExpenses(card.id)"
            :key="expense.id"
            class="flex items-center justify-between text-sm py-1.5 border-t border-rule"
          >
            <div class="min-w-0">
              <p class="truncate font-medium">{{ expense.description || expense.category_name }}</p>
              <p class="text-xs text-muted">{{ formatDate(expense.date) }} · {{ expense.category_name }}</p>
            </div>
            <p class="font-semibold tabular-nums shrink-0 ml-3">{{ formatCurrency(expense.amount) }}</p>
          </div>
          <p
            v-if="!creditCardStore.getExpenses(card.id).length"
            class="text-xs text-muted text-center py-2"
          >
            No expenses for this card yet.
          </p>
        </div>
      </PaperCard>
    </div>
  </div>
</template>
