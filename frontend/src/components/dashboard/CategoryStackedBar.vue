<script setup lang="ts">
import { computed } from 'vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import type { CategoryBarSegment } from '@/types'
import { useCurrency } from '@/composables/useCurrency'

const props = defineProps<{
  segments: CategoryBarSegment[]
  totalLabel?: string
  loading?: boolean
  error?: string | null
}>()

const { formatCurrency } = useCurrency()

const hasData = computed(() => props.segments.length > 0)

const sortedSegments = computed(() =>
  [...props.segments].sort((a, b) => b.amount - a.amount)
)

function segmentColor(segment: { colorIndex?: number; color?: string | null }): string {
  if (segment.color) return segment.color
  return `var(--cat-${segment.colorIndex || 1})`
}
</script>

<template>
  <PaperCard class="p-4 sm:p-5 md:p-6 animate-fade-up">
    <h2 class="section-title mb-1">Where it went</h2>
    <p class="text-xs text-muted mb-4 sm:mb-5">{{ totalLabel || 'This month' }}</p>

    <div v-if="loading" class="space-y-4 py-2">
      <div class="h-4 bg-paper-dark rounded-full animate-pulse" />
      <div class="space-y-2">
        <div v-for="n in 3" :key="n" class="h-3.5 bg-paper-dark rounded w-full animate-pulse" />
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

    <div v-else>
      <div class="flex h-4 rounded-full overflow-hidden bg-paper-dark">
        <div
          v-for="segment in sortedSegments"
          :key="segment.categoryId"
          :style="{
            width: `${segment.percentage}%`,
            backgroundColor: segmentColor(segment),
          }"
          class="h-full transition-all duration-700 first:rounded-l-full last:rounded-r-full"
          :title="`${segment.categoryName}: ${formatCurrency(segment.amount)}`"
        />
      </div>

      <div
        class="mt-4 sm:mt-5 grid gap-2.5"
        :class="sortedSegments.length <= 4
          ? 'grid-cols-1 sm:grid-cols-2'
          : 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3'
        "
      >
        <div
          v-for="segment in sortedSegments"
          :key="segment.categoryId"
          class="flex items-center gap-2.5 min-h-[44px] py-0.5"
        >
          <span
            class="w-2.5 h-2.5 rounded-full shrink-0"
            :style="{ backgroundColor: segmentColor(segment) }"
          />
          <div class="min-w-0 flex-1 flex items-baseline justify-between gap-2">
            <span class="text-xs sm:text-[0.8125rem] text-muted truncate">
              {{ segment.categoryName }}
            </span>
            <span class="text-xs sm:text-[0.8125rem] font-semibold tabular-nums text-ink shrink-0">
              {{ formatCurrency(segment.amount) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </PaperCard>
</template>
