<script setup lang="ts">
import { onMounted } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import FormField from '@/components/ui/FormField.vue'
import { formatCurrency } from '@/utils/format'
import { useDebtStore } from '@/stores/debts'
import { useForm } from '@/composables/useForm'
import type { DebtCreatePayload } from '@/types'

const debtStore = useDebtStore()

interface DebtForm {
  name: string
  description: string
  original_amount: number
  remaining_amount: number
  currency: string
  type: 'we_owe' | 'owed_to_us' | 'family_loan'
  counterparty_name: string
}

const initialForm: DebtForm = {
  name: '',
  description: '',
  original_amount: 0,
  remaining_amount: 0,
  currency: 'USD',
  type: 'we_owe',
  counterparty_name: '',
}

const { form, showForm, errorMessage, isSubmitting, toggleForm, handleSubmit } = useForm<DebtForm>({
  initialValues: initialForm,
  onSubmit: async (values) => {
    const payload: DebtCreatePayload = {
      name: values.name.trim(),
      description: values.description.trim() || null,
      original_amount: Number(values.original_amount),
      remaining_amount: Number(values.remaining_amount),
      currency: values.currency.trim().toUpperCase() || 'USD',
      type: values.type,
      counterparty_name: values.counterparty_name.trim() || null,
    }
    await debtStore.createDebt(payload)
  },
})

onMounted(async () => {
  await debtStore.fetchDebts()
})

function debtTypeLabel(type: DebtForm['type']): string {
  if (type === 'we_owe') return 'We owe'
  if (type === 'owed_to_us') return 'Owed to us'
  return 'Family loan'
}
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Debts" subtitle="What you owe and what you're owed.">
      <template #action>
        <button class="eb-btn" :class="showForm ? 'eb-btn-ghost' : 'eb-btn-primary'" @click="toggleForm">
          {{ showForm ? 'Cancel' : 'Add debt' }}
        </button>
      </template>
    </PageHeader>

    <form
      v-if="showForm"
      class="paper-card p-5 md:p-6 space-y-5 animate-fade-up"
      @submit.prevent="handleSubmit"
    >
      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <FormField label="Debt name" for-id="debt-name">
          <input
            id="debt-name"
            v-model="form.name"
            type="text"
            class="eb-input"
            maxlength="255"
            placeholder="e.g. Car loan"
            required
          />
        </FormField>

        <FormField label="Type" for-id="debt-type">
          <select id="debt-type" v-model="form.type" class="eb-select" required>
            <option value="we_owe">We owe</option>
            <option value="owed_to_us">Owed to us</option>
            <option value="family_loan">Family loan</option>
          </select>
        </FormField>

        <FormField label="Original amount" for-id="debt-original">
          <input
            id="debt-original"
            v-model.number="form.original_amount"
            type="number"
            class="eb-input"
            min="0.01"
            step="0.01"
            required
          />
        </FormField>

        <FormField label="Remaining amount" for-id="debt-remaining">
          <input
            id="debt-remaining"
            v-model.number="form.remaining_amount"
            type="number"
            class="eb-input"
            min="0"
            step="0.01"
            required
          />
        </FormField>

        <FormField label="Counterparty (optional)" for-id="debt-counterparty">
          <input
            id="debt-counterparty"
            v-model="form.counterparty_name"
            type="text"
            class="eb-input"
            maxlength="255"
            placeholder="e.g. Bank"
          />
        </FormField>

        <FormField label="Currency" for-id="debt-currency">
          <input
            id="debt-currency"
            v-model="form.currency"
            type="text"
            class="eb-input uppercase"
            maxlength="3"
            minlength="3"
            placeholder="USD"
            required
          />
        </FormField>

        <FormField label="Description (optional)" for-id="debt-description" class="md:col-span-2">
          <textarea
            id="debt-description"
            v-model="form.description"
            class="eb-input min-h-24"
            maxlength="1000"
            placeholder="Notes about this debt"
          />
        </FormField>
      </div>

      <p v-if="errorMessage" class="text-sm font-medium text-danger">{{ errorMessage }}</p>

      <div class="flex items-center gap-3">
        <button type="submit" class="eb-btn eb-btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving…' : 'Save debt' }}
        </button>
        <button type="button" class="eb-btn eb-btn-ghost" @click="showForm = false">Cancel</button>
      </div>
    </form>

    <div v-if="debtStore.loading" class="text-sm text-muted animate-pulse">Loading debts…</div>

    <!-- Mobile list -->
    <div v-else-if="debtStore.debts.length > 0" class="md:hidden space-y-3">
      <PaperCard
        v-for="debt in debtStore.debts"
        :key="debt.id"
        class="p-5 animate-fade-up"
      >
        <div class="flex items-start justify-between gap-3">
          <div>
            <h3 class="font-display text-xl tracking-tight">{{ debt.name }}</h3>
            <p class="text-sm text-muted mt-0.5">{{ debt.counterparty_name || 'No counterparty' }}</p>
          </div>
          <span class="chip" :class="debt.type === 'we_owe' ? 'chip-warn' : debt.type === 'owed_to_us' ? 'chip-sage' : 'chip-accent'">
            {{ debtTypeLabel(debt.type) }}
          </span>
        </div>
        <div class="grid grid-cols-2 gap-4 mt-5 text-sm">
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Original</p>
            <p class="font-medium tabular-nums mt-0.5">{{ formatCurrency(debt.original_amount) }}</p>
          </div>
          <div>
            <p class="text-xs text-muted uppercase tracking-wide">Remaining</p>
            <p class="font-semibold tabular-nums mt-0.5">{{ formatCurrency(debt.remaining_amount) }}</p>
          </div>
        </div>
      </PaperCard>
    </div>

    <!-- Desktop table -->
    <PaperCard v-else-if="debtStore.debts.length > 0" class="hidden md:block overflow-hidden animate-fade-up">
      <table class="table-editorial">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Counterparty</th>
            <th class="text-right">Original</th>
            <th class="text-right">Remaining</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="debt in debtStore.debts" :key="debt.id">
            <td class="font-medium">{{ debt.name }}</td>
            <td>
              <span class="chip" :class="debt.type === 'we_owe' ? 'chip-warn' : debt.type === 'owed_to_us' ? 'chip-sage' : 'chip-accent'">
                {{ debtTypeLabel(debt.type) }}
              </span>
            </td>
            <td class="text-muted">{{ debt.counterparty_name || '-' }}</td>
            <td class="text-right tabular-nums">{{ formatCurrency(debt.original_amount) }}</td>
            <td class="text-right font-semibold tabular-nums">{{ formatCurrency(debt.remaining_amount) }}</td>
            <td>
              <span
                class="chip"
                :class="debt.status === 'paid' ? 'chip-sage' : debt.status === 'defaulted' ? 'chip-danger' : 'chip-muted'"
              >
                {{ debt.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </PaperCard>

    <EmptyState v-else title="No debts recorded" description="Track loans and IOUs in one place.">
      <template #icon>📋</template>
      <template #action>
        <button class="eb-btn eb-btn-primary" @click="showForm = true">Add debt</button>
      </template>
    </EmptyState>
  </div>
</template>
