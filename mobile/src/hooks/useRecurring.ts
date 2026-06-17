import { useQuery } from "@tanstack/react-query"
import { api } from "@/services/api"

const RECURRING_KEY = ["recurring-expenses"] as const

export function useRecurringExpenses() {
  return useQuery({
    queryKey: RECURRING_KEY,
    queryFn: () => api.recurring.list(),
  })
}
