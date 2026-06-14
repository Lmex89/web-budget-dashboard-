import { defineStore } from 'pinia'
import { shallowRef, ref } from 'vue'
import type { CreditCard, CreditCardCreatePayload, ExpenseListItem } from '@/types'
import api from '@/services/api'

export const useCreditCardStore = defineStore('creditCards', () => {
  const creditCards = shallowRef<CreditCard[]>([])
  const cardExpenses = shallowRef<Record<string, ExpenseListItem[]>>({})
  const loading = ref(false)
  const loadingExpenses = ref(false)

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

  async function fetchCardExpenses(cardId: string) {
    loadingExpenses.value = true
    try {
      const { data } = await api.get('/api/v1/expenses', {
        params: { credit_card_id: cardId, page_size: 50 },
      })
      if (data.success) {
        cardExpenses.value = { ...cardExpenses.value, [cardId]: data.data }
      }
    } finally {
      loadingExpenses.value = false
    }
  }

  function getExpenses(cardId: string): ExpenseListItem[] {
    return cardExpenses.value[cardId] || []
  }

  return {
    creditCards,
    cardExpenses,
    loading,
    loadingExpenses,
    fetchCreditCards,
    createCreditCard,
    fetchCardExpenses,
    getExpenses,
  }
})
