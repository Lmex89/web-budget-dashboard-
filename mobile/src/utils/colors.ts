export const categoryColors: Record<string, string> = {
  food: "#ff9500",
  transport: "#007aff",
  housing: "#af52de",
  utilities: "#5ac8fa",
  entertainment: "#ff3b30",
  shopping: "#34c759",
  health: "#ff6482",
  education: "#5856d6",
  travel: "#00c7be",
  other: "#8e8e93",
}

export function getCategoryColor(color: string): string {
  return categoryColors[color] || color || "#8e8e93"
}

export const chartColors = [
  "#007aff",
  "#34c759",
  "#ff9500",
  "#ff3b30",
  "#af52de",
  "#5ac8fa",
  "#ff6482",
  "#5856d6",
  "#00c7be",
  "#8e8e93",
]

export const brandGradient = ["#007aff", "#5856d6"] as const
