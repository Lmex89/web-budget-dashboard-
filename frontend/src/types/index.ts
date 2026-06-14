export interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_admin: boolean
  family_id: string
  created_at: string
}

export interface ExpenseListItem {
  id: string
  amount: string
  description: string | null
  date: string
  payment_method: string
  category_name: string
  user_name: string
  created_at: string
}

export interface MonthlySummary {
  total_expenses: number
  year: number
  month: number
}

export interface CategoryDistribution {
  category: string
  color: string | null
  amount: number
}
