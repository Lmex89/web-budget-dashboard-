const BUDGET_PRESETS: Record<string, number> = {
  coche: 6139,
}

export function presetForCategory(name: string): number {
  const normalized = name.trim().toLowerCase()
  return BUDGET_PRESETS[normalized] ?? 0
}

export function hasBudgetPreset(name: string): boolean {
  return name.trim().toLowerCase() in BUDGET_PRESETS
}
