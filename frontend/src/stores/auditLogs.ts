import { defineStore } from 'pinia'
import { shallowRef, ref } from 'vue'
import type { AuditLog, FetchAuditLogsParams } from '@/types'
import api from '@/services/api'

export const useAuditLogStore = defineStore('auditLogs', () => {
  const auditLogs = shallowRef<AuditLog[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(25)
  const totalPages = ref(0)
  const filterEntityType = ref('')
  const filterAction = ref('')

  async function fetchAuditLogs(params?: FetchAuditLogsParams) {
    const requestParams: Record<string, string | number> = {
      page: params?.page || currentPage.value,
      page_size: params?.page_size || pageSize.value,
    }
    if (params?.entity_type || filterEntityType.value) {
      requestParams.entity_type = params?.entity_type || filterEntityType.value
    }
    if (params?.action || filterAction.value) {
      requestParams.action = params?.action || filterAction.value
    }

    const { data } = await api.get('/api/v1/audit-logs', { params: requestParams })
    if (data.success) {
      auditLogs.value = data.data
      total.value = data.total || 0
      currentPage.value = data.page || 1
      totalPages.value = data.total_pages || 0
    }
  }

  function clearFilters() {
    filterEntityType.value = ''
    filterAction.value = ''
  }

  return {
    auditLogs,
    total,
    currentPage,
    pageSize,
    totalPages,
    filterEntityType,
    filterAction,
    fetchAuditLogs,
    clearFilters,
  }
})
