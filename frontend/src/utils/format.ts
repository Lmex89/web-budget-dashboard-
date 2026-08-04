const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
})

const dateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
  year: 'numeric',
})

const shortDateFormatter = new Intl.DateTimeFormat('en-US', {
  month: 'short',
  day: 'numeric',
})

const monthFormatter = new Intl.DateTimeFormat('en-US', { month: 'long' })

export function formatCurrency(value: string | number | null | undefined): string {
  const num = Number(value)
  if (!Number.isFinite(num)) return '$0.00'
  return currencyFormatter.format(num)
}

export function formatDate(value: string | Date | null | undefined): string {
  if (!value) return '-'
  const dateStr = typeof value === 'string' ? value.split('T')[0] : value
  return dateFormatter.format(new Date(dateStr + 'T00:00:00'))
}

export function formatShortDate(value: string | Date | null | undefined): string {
  if (!value) return '-'
  const dateStr = typeof value === 'string' ? value.split('T')[0] : value
  return shortDateFormatter.format(new Date(dateStr + 'T00:00:00'))
}

export function formatMonthName(monthIndex: number): string {
  return monthFormatter.format(new Date(2000, monthIndex - 1, 1))
}

export function clamp(num: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, num))
}
