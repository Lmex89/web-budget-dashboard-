import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Debt, DebtCreatePayload } from '@/types'
import api from '@/services/api'

export const useDebtStore = defineStore('debts', () => {
  const debts = ref<Debt[]>([])
  const loading = ref(false)

  async function fetchDebts() {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/debts')
      if (data.success) {
        debts.value = data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function createDebt(payload: DebtCreatePayload) {
    const { data } = await api.post('/api/v1/debts', payload)
    if (data.success) {
      debts.value = [data.data, ...debts.value]
    }
    return data
  }

  return {
    debts,
    loading,
    fetchDebts,
    createDebt,
  }
})
