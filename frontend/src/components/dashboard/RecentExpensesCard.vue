<script setup lang="ts">
import { ref } from 'vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import type { DashboardExpense } from '@/types'
import { useCurrency } from '@/composables/useCurrency'
import { formatShortDate } from '@/utils/format'

defineProps<{
  expenses: DashboardExpense[]
  loading?: boolean
  error?: string | null
}>()

const emit = defineEmits<{
  (e: 'delete', id: string): void
}>()

const confirmingDeleteId = ref<string | null>(null)

function promptDelete(id: string) {
  confirmingDeleteId.value = id
}

function cancelDelete() {
  confirmingDeleteId.value = null
}

function confirmDelete(id: string) {
  confirmingDeleteId.value = null
  emit('delete', id)
}

const { formatCurrency } = useCurrency()
</script>

<template>
  <PaperCard class="p-4 sm:p-5 md:p-6 animate-fade-up min-h-0">
    <div class="flex items-center justify-between mb-4 sm:mb-5">
      <h2 class="section-title">Recent expenses</h2>
      <router-link
        to="/expenses"
        class="text-xs font-semibold text-accent hover:underline py-2 -my-2 px-1"
      >
        View all
      </router-link>
    </div>

    <div v-if="loading" class="space-y-3 py-1">
      <div v-for="n in 5" :key="n" class="flex items-center justify-between gap-3 py-2">
        <div class="flex-1 space-y-1.5">
          <div class="h-3.5 bg-paper-dark rounded w-3/4 animate-pulse" />
          <div class="h-3 bg-paper-dark rounded w-2/5 animate-pulse" />
        </div>
        <div class="h-3.5 bg-paper-dark rounded w-14 shrink-0 animate-pulse" />
      </div>
    </div>

    <div v-else-if="error" class="py-8 text-center">
      <p class="text-sm text-danger">{{ error }}</p>
    </div>

    <div v-else-if="expenses.length === 0" class="py-4">
      <EmptyState title="Nothing here" description="Track a new expense and it will appear here.">
        <template #icon>💰</template>
        <template #action>
          <router-link to="/expenses" class="eb-btn eb-btn-ghost">Add one</router-link>
        </template>
      </EmptyState>
    </div>

    <div v-else class="divide-y divide-rule -mx-1">
      <div
        v-for="expense in expenses"
        :key="expense.id"
        class="flex items-center justify-between py-3 px-1 gap-3 min-h-[44px]"
      >
        <div class="min-w-0 flex-1">
          <p class="text-[0.9375rem] font-medium truncate leading-snug">{{ expense.description }}</p>
          <p class="text-xs text-muted mt-0.5">
            {{ expense.authorName }} · {{ formatShortDate(expense.date) }}
          </p>
        </div>
        <div class="text-right shrink-0">
          <span class="text-[0.9375rem] font-semibold tabular-nums text-ink block">
            {{ formatCurrency(expense.amount) }}
          </span>
          <div v-if="confirmingDeleteId === expense.id" class="flex items-center justify-end gap-2 mt-1">
            <button
              class="text-xs font-semibold text-danger hover:underline"
              @click="confirmDelete(expense.id)"
            >
              Confirm
            </button>
            <button
              class="text-xs text-muted hover:underline"
              @click="cancelDelete"
            >
              Cancel
            </button>
          </div>
          <button
            v-else
            class="text-xs text-danger hover:underline mt-1"
            @click="promptDelete(expense.id)"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </PaperCard>
</template>
