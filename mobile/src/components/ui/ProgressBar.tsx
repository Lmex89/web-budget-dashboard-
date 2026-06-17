import { View } from "react-native"
import { cn } from "@/utils/cn"

interface ProgressBarProps {
  value: number
  max?: number
  className?: string
  barClassName?: string
  color?: string
}

export function ProgressBar({
  value,
  max = 100,
  className,
  barClassName,
  color,
}: ProgressBarProps) {
  const pct = Math.min(Math.max(value / max, 0), 1)

  return (
    <View
      className={cn("h-2 overflow-hidden rounded-full bg-border dark:bg-border-dark", className)}
      accessibilityRole="progressbar"
      accessibilityValue={{ min: 0, max, now: value }}
    >
      <View
        className={cn("h-full rounded-full", barClassName)}
        style={{
          width: `${pct * 100}%`,
          backgroundColor: color,
        }}
      />
    </View>
  )
}
