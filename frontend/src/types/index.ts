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

export interface Category {
  id: string
  name: string
  color: string | null
  icon: string | null
  family_id: string
  parent_id: string | null
  created_at: string
}

export interface CreditCard {
  id: string
  name: string
  last_four_digits: string | null
  limit: string | number
  closing_day: number
  due_day: number
  current_balance: string | number
  family_id: string
  created_at: string
  updated_at: string
}

export interface CreditCardCreatePayload {
  name: string
  last_four_digits?: string | null
  limit: number
  closing_day: number
  due_day: number
  current_balance?: number
}
