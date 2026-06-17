import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { api } from "@/services/api"
import { useFilterStore } from "@/stores/useFilterStore"
import type { Transaction } from "@/types"

const TRANSACTIONS_KEY = ["transactions"] as const

export function useTransactions() {
  const filters = useFilterStore((s) => s.filters)

  return useQuery({
    queryKey: [...TRANSACTIONS_KEY, filters],
    queryFn: () => api.transactions.list(filters),
    select: (data) => data.data,
  })
}

export function useTransaction(id: string) {
  return useQuery({
    queryKey: [...TRANSACTIONS_KEY, id],
    queryFn: () => api.transactions.get(id),
    enabled: !!id,
  })
}

export function useCreateTransaction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Transaction>) => api.transactions.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY })
    },
  })
}

export function useDeleteTransaction() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.transactions.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: TRANSACTIONS_KEY })
    },
  })
}
