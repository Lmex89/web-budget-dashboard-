<script setup lang="ts">
import PaperCard from '@/components/ui/PaperCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import type { CategoryBarSegment } from '@/types'
import { useCurrency } from '@/composables/useCurrency'

defineProps<{
  categories: CategoryBarSegment[]
  loading?: boolean
  error?: string | null
}>()

const { formatCurrency } = useCurrency()

function segmentColor(index: number): string {
  return `var(--cat-${index})`
}
</script>

<template>
  <PaperCard class="p-4 sm:p-5 md:p-6 animate-fade-up min-h-0">
    <h2 class="section-title mb-4 sm:mb-5">Top categories</h2>

    <div v-if="loading" class="space-y-3 py-1">
      <div v-for="n in 4" :key="n" class="flex items-center gap-3 py-2">
        <div class="w-2.5 h-2.5 rounded-full bg-paper-dark animate-pulse shrink-0" />
        <div class="flex-1 h-3.5 bg-paper-dark rounded animate-pulse" />
        <div class="h-3.5 bg-paper-dark rounded w-16 shrink-0 animate-pulse" />
      </div>
    </div>

    <div v-else-if="error" class="py-8 text-center">
      <p class="text-sm text-danger">{{ error }}</p>
    </div>

    <div v-else-if="categories.length === 0" class="py-4">
      <EmptyState title="No categories" description="Add expenses to see your top categories.">
        <template #icon>🏷️</template>
      </EmptyState>
    </div>

    <div v-else class="space-y-0.5 -mx-1">
      <div
        v-for="cat in categories"
        :key="cat.categoryId"
        class="flex items-center justify-between py-2.5 px-1 gap-3 min-h-[44px]"
      >
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <span
            class="w-2.5 h-2.5 rounded-full shrink-0"
            :style="{ backgroundColor: segmentColor(cat.colorIndex) }"
          />
          <span class="text-[0.9375rem] font-medium truncate">{{ cat.categoryName }}</span>
        </div>
        <span class="text-[0.9375rem] font-semibold tabular-nums text-ink shrink-0">
          {{ formatCurrency(cat.amount) }}
        </span>
      </div>
    </div>
  </PaperCard>
</template>
