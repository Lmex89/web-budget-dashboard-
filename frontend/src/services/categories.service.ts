import type { DashboardCategory } from '@/types'

function delay(ms = 300): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

const SAMPLE_CATEGORIES: DashboardCategory[] = [
  { id: 'cat-1', name: 'Entretenimiento', colorIndex: 1 },
  { id: 'cat-2', name: 'Tdc Vexi Ñuis', colorIndex: 2 },
  { id: 'cat-3', name: 'TDC Banamex ORO', colorIndex: 3 },
  { id: 'cat-4', name: 'TDC INVEX Luis', colorIndex: 4 },
  { id: 'cat-5', name: 'Comida', colorIndex: 5 },
  { id: 'cat-6', name: 'Tarjeta vexi alma', colorIndex: 1 },
  { id: 'cat-7', name: 'Varios', colorIndex: 2 },
  { id: 'cat-8', name: 'Mutualista', colorIndex: 3 },
  { id: 'cat-9', name: 'Salud', colorIndex: 4 },
  { id: 'cat-10', name: 'Coche', colorIndex: 5 },
  { id: 'cat-11', name: 'Transporte', colorIndex: 1 },
]

export async function fetchDashboardCategories(): Promise<DashboardCategory[]> {
  await delay()
  return SAMPLE_CATEGORIES
}
