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
  credit_card_id: string | null
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

export interface CreateExpensePayload {
  amount: number
  description: string
  date: string
  payment_method: string
  category_id: string
  is_installment: boolean
  total_installments: number | null
  credit_card_id?: string | null
}

export interface CreateCategoryPayload {
  name: string
  color?: string | null
  icon?: string | null
}

export interface UpdateCategoryPayload {
  name: string
}

export interface CreditCardCreatePayload {
  name: string
  last_four_digits?: string | null
  limit: number
  closing_day: number
  due_day: number
  current_balance?: number
}

export interface CreateMemberPayload {
  email: string
  password: string
  full_name: string
}

export interface RegisterPayload {
  email: string
  password: string
  full_name: string
  family_name: string
}

export interface Debt {
  id: string
  name: string
  description: string | null
  original_amount: string | number
  remaining_amount: string | number
  currency: string
  type: 'we_owe' | 'owed_to_us' | 'family_loan'
  status: 'active' | 'paid' | 'defaulted'
  counterparty_name: string | null
  family_id: string
  created_by_user_id: string
  created_at: string
  updated_at: string
}

export interface DebtCreatePayload {
  name: string
  description?: string | null
  original_amount: number
  remaining_amount?: number | null
  currency?: string
  type: 'we_owe' | 'owed_to_us' | 'family_loan'
  status?: 'active' | 'paid' | 'defaulted'
  counterparty_name?: string | null
}

export interface DashboardExpense {
  id: string
  description: string
  amount: number
  date: string
  categoryId: string
  authorName: string
}

export interface DashboardCategory {
  id: string
  name: string
  colorIndex: 1 | 2 | 3 | 4 | 5
}

export interface DashboardSummary {
  totalExpenses: number
  categoriesUsedCount: number
  familyMembersCount: number
  month: number
  year: number
}

export interface CategoryBarSegment {
  categoryId: string
  categoryName: string
  amount: number
  percentage: number
  colorIndex: 1 | 2 | 3 | 4 | 5
}

export interface StatCardData {
  label: string
  value: string
  caption: string
  tone: 'ink' | 'accent' | 'sage'
}
