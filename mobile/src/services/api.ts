import type {
  Transaction,
  Category,
  Budget,
  RecurringExpense,
  CashFlowPoint,
  PaginatedResponse,
  TransactionFilters,
} from "@/types"

const BASE_URL = "http://localhost:8000/api/v1"

class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message)
    this.name = "ApiError"
  }
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${BASE_URL}${path}`
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new ApiError(
      response.status,
      body?.detail || `Request failed: ${response.status}`,
    )
  }

  return response.json()
}

function buildQueryString(filters: Partial<TransactionFilters>): string {
  const params = new URLSearchParams()
  if (filters.search) params.set("search", filters.search)
  if (filters.category_id) params.set("category_id", filters.category_id)
  if (filters.type) params.set("type", filters.type)
  if (filters.start_date) params.set("start_date", filters.start_date)
  if (filters.end_date) params.set("end_date", filters.end_date)
  if (filters.sort_by) params.set("sort_by", filters.sort_by)
  if (filters.sort_order) params.set("sort_order", filters.sort_order)
  const qs = params.toString()
  return qs ? `?${qs}` : ""
}

export const api = {
  transactions: {
    list: (filters?: TransactionFilters) =>
      request<PaginatedResponse<Transaction>>(
        `/transactions${filters ? buildQueryString(filters) : ""}`,
      ),

    get: (id: string) => request<Transaction>(`/transactions/${id}`),

    create: (data: Partial<Transaction>) =>
      request<Transaction>("/transactions", {
        method: "POST",
        body: JSON.stringify(data),
      }),

    delete: (id: string) =>
      request<void>(`/transactions/${id}`, { method: "DELETE" }),
  },

  categories: {
    list: () => request<Category[]>("/categories"),
  },

  budgets: {
    get: (month: number, year: number) =>
      request<Budget>(`/budgets?month=${month}&year=${year}`),
  },

  recurring: {
    list: () => request<RecurringExpense[]>("/recurring-expenses"),
  },

  analytics: {
    cashFlow: (months: number = 6) =>
      request<CashFlowPoint[]>(`/analytics/cash-flow?months=${months}`),

    monthlySpending: (month: number, year: number) =>
      request<{ total: number; previous_total: number; change_pct: number }>(
        `/analytics/monthly-spending?month=${month}&year=${year}`,
      ),
  },
}
