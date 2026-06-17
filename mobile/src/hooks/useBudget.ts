import { useQuery } from "@tanstack/react-query"
import { api } from "@/services/api"

function getCurrentMonthYear() {
  const now = new Date()
  return { month: now.getMonth() + 1, year: now.getFullYear() }
}

const BUDGET_KEY = ["budget"] as const

export function useBudget(month?: number, year?: number) {
  const params = month && year ? { month, year } : getCurrentMonthYear()

  return useQuery({
    queryKey: [...BUDGET_KEY, params.month, params.year],
    queryFn: () => api.budgets.get(params.month, params.year),
  })
}
