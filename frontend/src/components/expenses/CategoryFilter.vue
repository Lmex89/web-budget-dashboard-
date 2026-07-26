<script setup lang="ts">
import type { Category } from '@/types'

const props = defineProps<{
  selectedIds: string[]
  categories: Category[]
}>()

const emit = defineEmits<{
  (e: 'update:selectedIds', ids: string[]): void
}>()

function isSelected(id: string) {
  return props.selectedIds.includes(id)
}

function toggle(id: string) {
  const set = new Set(props.selectedIds)
  if (set.has(id)) {
    set.delete(id)
  } else {
    set.add(id)
  }
  emit('update:selectedIds', Array.from(set))
}

function clearAll() {
  emit('update:selectedIds', [])
}
</script>

<template>
  <div class="space-y-2">
    <div class="flex items-center justify-between">
      <span class="eb-label mb-0">Categories</span>
      <button
        v-if="selectedIds.length > 0"
        type="button"
        class="text-xs font-medium text-accent hover:underline"
        @click="clearAll"
      >
        Clear
      </button>
    </div>
    <div class="flex flex-wrap gap-2 max-h-36 overflow-y-auto pr-1">
      <label
        v-for="category in categories"
        :key="category.id"
        class="cursor-pointer select-none"
      >
        <input
          type="checkbox"
          class="sr-only peer"
          :checked="isSelected(category.id)"
          @change="toggle(category.id)"
        />
        <span
          class="chip transition-all duration-200 peer-focus:ring-2 peer-focus:ring-accent peer-focus:ring-offset-2"
          :class="isSelected(category.id) ? 'chip-accent' : 'chip-muted'"
        >
          {{ category.name }}
        </span>
      </label>
    </div>
  </div>
</template>
