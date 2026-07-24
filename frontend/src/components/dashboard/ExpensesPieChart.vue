<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js'
import PaperCard from '@/components/ui/PaperCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import type { CategoryBarSegment } from '@/types'
import { useCurrency } from '@/composables/useCurrency'

ChartJS.register(ArcElement, Tooltip, Legend)

const props = defineProps<{
  segments: CategoryBarSegment[]
  totalLabel?: string
  loading?: boolean
  error?: string | null
}>()

const { formatCurrency } = useCurrency()

const hasData = computed(() => props.segments.length > 0)

const totalAmount = computed(() =>
  props.segments.reduce((sum, s) => sum + s.amount, 0)
)

const sortedSegments = computed(() =>
  [...props.segments].sort((a, b) => b.amount - a.amount)
)

const chartData = computed(() => {
  const sorted = sortedSegments.value
  return {
    labels: sorted.map(s => s.categoryName),
    datasets: [
      {
        data: sorted.map(s => s.amount),
        backgroundColor: sorted.map(s => s.color),
        borderWidth: 0,
        hoverOffset: 10,
      },
    ],
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: true,
  cutout: '65%',
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'var(--paper-2)',
      titleColor: 'var(--ink)',
      bodyColor: 'var(--ink)',
      borderColor: 'var(--rule)',
      borderWidth: 1,
      padding: 12,
      cornerRadius: 8,
      displayColors: true,
      boxPadding: 4,
      callbacks: {
        title(ctx: { label?: string }[]) {
          return ctx[0]?.label ?? ''
        },
        label(ctx: { parsed: number; dataset: { data: number[] } }) {
          const total = ctx.dataset.data.reduce((a: number, b: number) => a + b, 0)
          const pct = total > 0 ? ((ctx.parsed / total) * 100).toFixed(1) : '0.0'
          return ` ${formatCurrency(ctx.parsed)}  (${pct}%)`
        },
      },
    },
  },
}))

function pct(amount: number): string {
  if (!totalAmount.value) return '0.0'
  return ((amount / totalAmount.value) * 100).toFixed(1)
}
</script>

<template>
  <PaperCard class="p-4 sm:p-5 md:p-6 animate-fade-up">
    <h2 class="section-title mb-1">Expenses distribution</h2>
    <p class="text-xs text-muted mb-4 sm:mb-5">{{ totalLabel || 'This month' }}</p>

    <div v-if="loading" class="flex flex-col items-center py-8">
      <div class="w-48 h-48 rounded-full bg-paper-dark animate-pulse" />
      <div class="mt-6 space-y-2 w-full max-w-xs">
        <div v-for="n in 4" :key="n" class="h-3.5 bg-paper-dark rounded w-full animate-pulse" />
      </div>
    </div>

    <div v-else-if="error" class="py-8 text-center">
      <p class="text-sm text-danger">{{ error }}</p>
    </div>

    <div v-else-if="!hasData" class="py-4">
      <EmptyState
        title="No data yet"
        description="Add expenses to see your spending breakdown."
      >
        <template #icon>📊</template>
      </EmptyState>
    </div>

    <div v-else class="flex flex-col lg:flex-row items-center gap-6 lg:gap-10">
      <div class="relative w-48 h-48 sm:w-56 sm:h-56 shrink-0">
        <Doughnut :data="chartData" :options="chartOptions" />
        <div
          class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
        >
          <span class="text-[10px] uppercase tracking-wide text-muted">Total</span>
          <span class="text-base sm:text-lg font-semibold tabular-nums text-ink">
            {{ formatCurrency(totalAmount) }}
          </span>
        </div>
      </div>

      <div class="flex-1 w-full min-w-0">
        <div class="space-y-2.5">
          <div
            v-for="segment in sortedSegments"
            :key="segment.categoryId"
            class="flex items-center gap-3 min-h-[36px]"
          >
            <span
              class="w-2.5 h-2.5 rounded-full shrink-0"
              :style="{ backgroundColor: segment.color }"
            />
            <div class="min-w-0 flex-1 flex items-baseline justify-between gap-2">
              <span class="text-sm text-muted truncate">
                {{ segment.categoryName }}
              </span>
              <span class="text-xs font-semibold tabular-nums text-muted shrink-0">
                {{ pct(segment.amount) }}%
              </span>
            </div>
            <span class="text-sm font-semibold tabular-nums text-ink shrink-0 w-24 text-right hidden sm:block">
              {{ formatCurrency(segment.amount) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </PaperCard>
</template>
