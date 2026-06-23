export function useCurrency() {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })

  function formatCurrency(value: number): string {
    return formatter.format(value)
  }

  return { formatCurrency }
}
