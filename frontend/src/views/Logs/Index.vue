<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useAuditLogStore } from '@/stores/auditLogs'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { formatDate } from '@/utils/format'
import type { AuditLog } from '@/types'

const auditLogStore = useAuditLogStore()

const entityTypeOptions = [
  { value: '', label: 'All entities' },
  { value: 'expense', label: 'Expense' },
  { value: 'category', label: 'Category' },
  { value: 'credit_card', label: 'Credit Card' },
  { value: 'debt', label: 'Debt' },
]

const actionOptions = [
  { value: '', label: 'All actions' },
  { value: 'create', label: 'Create' },
  { value: 'update', label: 'Update' },
  { value: 'delete', label: 'Delete' },
]

const hasActiveFilters = computed(
  () => auditLogStore.filterEntityType || auditLogStore.filterAction
)

async function applyFilters() {
  await auditLogStore.fetchAuditLogs({ page: 1 })
}

async function clearFilters() {
  auditLogStore.clearFilters()
  await auditLogStore.fetchAuditLogs({ page: 1 })
}

async function goToPage(page: number) {
  await auditLogStore.fetchAuditLogs({ page })
}

const visiblePages = computed(() => {
  const tp = auditLogStore.totalPages
  if (tp <= 7) return Array.from({ length: tp }, (_, i) => i + 1)
  const cp = auditLogStore.currentPage
  const pages: (number | string)[] = [1]
  if (cp > 3) pages.push('...')
  for (let i = Math.max(2, cp - 1); i <= Math.min(tp - 1, cp + 1); i++) {
    pages.push(i)
  }
  if (cp < tp - 2) pages.push('...')
  pages.push(tp)
  return pages
})

function actionClass(action: string): string {
  switch (action) {
    case 'create':
      return 'chip-sage'
    case 'update':
      return 'chip-accent'
    case 'delete':
      return 'chip-danger'
    default:
      return 'chip-muted'
  }
}

function previewChanges(log: AuditLog): string {
  const values = log.action === 'delete' ? log.old_values : log.new_values
  if (!values) return '-'
  const entries = Object.entries(values)
    .filter(([, v]) => v !== null && v !== undefined)
    .slice(0, 3)
  return entries.map(([k, v]) => `${k}: ${String(v)}`).join(', ')
}

onMounted(() => {
  auditLogStore.fetchAuditLogs()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Audit logs" subtitle="Track every change made in your family budget.">
      <template #action>
        <button class="eb-btn eb-btn-ghost text-sm" @click="auditLogStore.fetchAuditLogs({ page: 1 })">
          Refresh
        </button>
      </template>
    </PageHeader>

    <PaperCard class="p-4">
      <div class="flex flex-wrap items-end gap-3">
        <div class="flex flex-col gap-1">
          <label class="eb-label text-xs">Entity</label>
          <select v-model="auditLogStore.filterEntityType" class="eb-select w-40">
            <option v-for="opt in entityTypeOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
        <div class="flex flex-col gap-1">
          <label class="eb-label text-xs">Action</label>
          <select v-model="auditLogStore.filterAction" class="eb-select w-40">
            <option v-for="opt in actionOptions" :key="opt.value" :value="opt.value">
              {{ opt.label }}
            </option>
          </select>
        </div>
        <button class="eb-btn eb-btn-primary text-sm" @click="applyFilters">
          Apply
        </button>
        <button
          v-if="hasActiveFilters"
          class="eb-btn eb-btn-ghost text-sm"
          @click="clearFilters"
        >
          Clear
        </button>
      </div>
    </PaperCard>

    <div v-if="auditLogStore.auditLogs.length > 0" class="md:hidden space-y-3">
      <PaperCard
        v-for="log in auditLogStore.auditLogs"
        :key="log.id"
        class="p-4 flex flex-col gap-2 animate-fade-up"
      >
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <span class="chip" :class="actionClass(log.action)">{{ log.action }}</span>
            <span class="text-sm font-medium capitalize">{{ log.entity_type }}</span>
          </div>
          <span class="text-xs text-muted">{{ formatDate(log.created_at) }}</span>
        </div>
        <p class="text-sm text-muted">
          By <span class="font-medium text-ink">{{ log.user_name }}</span>
        </p>
        <p class="text-xs text-muted truncate" :title="previewChanges(log)">
          {{ previewChanges(log) }}
        </p>
      </PaperCard>
    </div>

    <PaperCard v-if="auditLogStore.auditLogs.length > 0" class="hidden md:block overflow-hidden animate-fade-up">
      <table class="table-editorial">
        <thead>
          <tr>
            <th>Date</th>
            <th>User</th>
            <th>Action</th>
            <th>Entity</th>
            <th>Entity ID</th>
            <th>Changes</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in auditLogStore.auditLogs" :key="log.id">
            <td class="text-muted whitespace-nowrap">{{ formatDate(log.created_at) }}</td>
            <td class="font-medium">{{ log.user_name }}</td>
            <td>
              <span class="chip" :class="actionClass(log.action)">{{ log.action }}</span>
            </td>
            <td class="capitalize">{{ log.entity_type }}</td>
            <td class="font-mono text-xs text-muted">{{ log.entity_id }}</td>
            <td class="text-muted truncate max-w-xs" :title="previewChanges(log)">
              {{ previewChanges(log) }}
            </td>
          </tr>
        </tbody>
      </table>
    </PaperCard>

    <nav v-if="auditLogStore.totalPages > 1" class="flex items-center justify-center gap-1 animate-fade-up" aria-label="Pagination">
      <button
        class="eb-btn eb-btn-ghost text-sm px-2"
        :disabled="auditLogStore.currentPage <= 1"
        @click="goToPage(auditLogStore.currentPage - 1)"
      >
        Prev
      </button>
      <template v-for="p in visiblePages" :key="p">
        <span v-if="p === '...'" class="px-1 text-muted text-sm">...</span>
        <button
          v-else
          class="eb-btn text-sm px-3"
          :class="p === auditLogStore.currentPage ? 'eb-btn-primary' : 'eb-btn-ghost'"
          @click="goToPage(p as number)"
        >
          {{ p }}
        </button>
      </template>
      <button
        class="eb-btn eb-btn-ghost text-sm px-2"
        :disabled="auditLogStore.currentPage >= auditLogStore.totalPages"
        @click="goToPage(auditLogStore.currentPage + 1)"
      >
        Next
      </button>
    </nav>

    <EmptyState
      v-if="auditLogStore.auditLogs.length === 0"
      title="No audit logs yet"
      description="Changes to expenses, categories, and other records will appear here."
    >
      <template #icon>📝</template>
    </EmptyState>
  </div>
</template>
