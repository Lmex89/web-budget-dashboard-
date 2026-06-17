// ── Domain Models ──

export interface Transaction {
  id: string
  amount: number
  description: string
  category_id: string
  category_name: string
  category_icon: string
  date: string
  type: "income" | "expense"
  payment_method: "cash" | "debit" | "credit"
  is_recurring: boolean
  recurring_id?: string
  user_name: string
  created_at: string
}

export interface Category {
  id: string
  name: string
  icon: string
  color: string
  budgeted: number
  spent: number
  type: "income" | "expense"
}

export interface Budget {
  id: string
  month: number
  year: number
  total_budgeted: number
  total_spent: number
  categories: CategoryBudget[]
}

export interface CategoryBudget {
  category_id: string
  category_name: string
  category_icon: string
  category_color: string
  budgeted: number
  spent: number
}

export interface RecurringExpense {
  id: string
  description: string
  amount: number
  category_id: string
  category_name: string
  category_icon: string
  frequency: "weekly" | "biweekly" | "monthly" | "quarterly" | "yearly"
  next_due: string
  status: "active" | "paused" | "cancelled"
  payment_method: string
}

export interface CashFlowPoint {
  date: string
  income: number
  expense: number
  balance: number
}

// ── API Response Wrappers ──

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
}

// ── Filter & Search ──

export interface TransactionFilters {
  search: string
  category_id?: string
  type?: "income" | "expense"
  start_date?: string
  end_date?: string
  sort_by?: "date" | "amount"
  sort_order?: "asc" | "desc"
}

// ── Store State Types ──

export type ThemeMode = "light" | "dark" | "system"

export interface ThemeState {
  mode: ThemeMode
  isDark: boolean
  setMode: (mode: ThemeMode) => void
  toggle: () => void
}

export interface FilterState {
  filters: TransactionFilters
  setSearch: (search: string) => void
  setCategoryFilter: (category_id?: string) => void
  setTypeFilter: (type?: "income" | "expense") => void
  setDateRange: (start?: string, end?: string) => void
  setSort: (by: "date" | "amount", order: "asc" | "desc") => void
  clearFilters: () => void
}
