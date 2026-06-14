import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { CreditCard, CreditCardCreatePayload } from '@/types'
import api from '@/services/api'

export const useCreditCardStore = defineStore('creditCards', () => {
  const creditCards = ref<CreditCard[]>([])
  const loading = ref(false)

  async function fetchCreditCards() {
    loading.value = true
    try {
      const { data } = await api.get('/api/v1/credit-cards')
      if (data.success) {
        creditCards.value = data.data
      }
    } finally {
      loading.value = false
    }
  }

  async function createCreditCard(payload: CreditCardCreatePayload) {
    const { data } = await api.post('/api/v1/credit-cards', payload)
    if (data.success) {
      creditCards.value = [data.data, ...creditCards.value]
    }
    return data
  }

  return {
    creditCards,
    loading,
    fetchCreditCards,
    createCreditCard,
  }
})
