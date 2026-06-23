import type { DashboardExpense, DashboardSummary, CategoryBarSegment } from '@/types'

function delay(ms = 400): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const SAMPLE_EXPENSES: DashboardExpense[] = [
  { id: 'e1', description: 'pepsi, tortilla, agua', amount: 95, date: '2026-06-22', categoryId: 'cat-5', authorName: 'Admin User' },
  { id: 'e2', description: 'cena pizzas', amount: 140, date: '2026-06-21', categoryId: 'cat-5', authorName: 'Admin User' },
  { id: 'e3', description: 'Cochinita desayuno', amount: 200, date: '2026-06-21', categoryId: 'cat-5', authorName: 'Admin User' },
  { id: 'e4', description: 'Limosna', amount: 100, date: '2026-06-21', categoryId: 'cat-7', authorName: 'Admin User' },
  { id: 'e5', description: 'tostadas para fiesta ahijado', amount: 270, date: '2026-06-21', categoryId: 'cat-5', authorName: 'Admin User' },
]

const SAMPLE_SUMMARY: DashboardSummary = {
  totalExpenses: 23274,
  categoriesUsedCount: 11,
  familyMembersCount: 1,
  month: 6,
  year: 2026,
}

const SAMPLE_SEGMENTS: CategoryBarSegment[] = [
  { categoryId: 'cat-1', categoryName: 'Entretenimiento', amount: 7791, percentage: 0, colorIndex: 1 },
  { categoryId: 'cat-2', categoryName: 'Tdc Vexi Ñuis', amount: 4350, percentage: 0, colorIndex: 2 },
  { categoryId: 'cat-3', categoryName: 'TDC Banamex ORO', amount: 4250, percentage: 0, colorIndex: 3 },
  { categoryId: 'cat-4', categoryName: 'TDC INVEX Luis', amount: 1600, percentage: 0, colorIndex: 4 },
  { categoryId: 'cat-5', categoryName: 'Comida', amount: 1122, percentage: 0, colorIndex: 5 },
  { categoryId: 'cat-6', categoryName: 'Tarjeta vexi alma', amount: 1000, percentage: 0, colorIndex: 1 },
  { categoryId: 'cat-7', categoryName: 'Varios', amount: 970, percentage: 0, colorIndex: 2 },
  { categoryId: 'cat-8', categoryName: 'Mutualista', amount: 750, percentage: 0, colorIndex: 3 },
  { categoryId: 'cat-9', categoryName: 'Salud', amount: 580, percentage: 0, colorIndex: 4 },
  { categoryId: 'cat-10', categoryName: 'Coche', amount: 440, percentage: 0, colorIndex: 5 },
  { categoryId: 'cat-11', categoryName: 'Transporte', amount: 421, percentage: 0, colorIndex: 1 },
]

export async function fetchDashboardExpenses(): Promise<DashboardExpense[]> {
  await delay()
  return SAMPLE_EXPENSES
}

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  await delay()
  return SAMPLE_SUMMARY
}

export async function fetchCategorySegments(): Promise<CategoryBarSegment[]> {
  await delay()
  return SAMPLE_SEGMENTS
}
