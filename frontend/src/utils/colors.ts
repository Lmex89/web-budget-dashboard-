export const CATEGORY_COLORS_LIGHT = [
  '#f97316',
  '#3b82f6',
  '#22c55e',
  '#a855f7',
  '#ec4899',
  '#0ea5e9',
  '#f59e0b',
  '#14b8a6',
  '#8b5cf6',
  '#f43f5e',
  '#06b6d4',
  '#84cc16',
]

export const CATEGORY_COLORS_DARK = [
  '#fb923c',
  '#60a5fa',
  '#4ade80',
  '#c084fc',
  '#f472b6',
  '#38bdf8',
  '#fbbf24',
  '#2dd4bf',
  '#a78bfa',
  '#fb7185',
  '#22d3ee',
  '#a3e635',
]

export function isDarkMode(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

export function getCategoryColor(index: number): string {
  const palette = isDarkMode() ? CATEGORY_COLORS_DARK : CATEGORY_COLORS_LIGHT
  return palette[index % palette.length]
}

export function getSegmentColor(segment: { color?: string }): string {
  return segment.color || CATEGORY_COLORS_LIGHT[0]
}
