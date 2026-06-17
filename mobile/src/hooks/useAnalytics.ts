import { useQuery } from "@tanstack/react-query"
import { api } from "@/services/api"

export function useCashFlow(months: number = 6) {
  return useQuery({
    queryKey: ["cash-flow", months],
    queryFn: () => api.analytics.cashFlow(months),
  })
}

export function useMonthlySpending(month?: number, year?: number) {
  const now = new Date()
  const m = month ?? now.getMonth() + 1
  const y = year ?? now.getFullYear()

  return useQuery({
    queryKey: ["monthly-spending", m, y],
    queryFn: () => api.analytics.monthlySpending(m, y),
  })
}
