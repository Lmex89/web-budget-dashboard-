import { TouchableOpacity, Text } from "react-native"
import { cn } from "@/utils/cn"

interface FilterChipProps {
  label: string
  selected?: boolean
  onPress: () => void
}

export function FilterChip({ label, selected = false, onPress }: FilterChipProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      accessibilityRole="button"
      accessibilityState={{ selected }}
      accessibilityLabel={`Filter by ${label}`}
      className={cn(
        "rounded-full px-4 py-2",
        selected
          ? "bg-accent-blue"
          : "bg-card dark:bg-card-dark",
      )}
    >
      <Text
        className={cn(
          "text-sm font-medium",
          selected ? "text-white" : "text-ink dark:text-ink-dark",
        )}
      >
        {label}
      </Text>
    </TouchableOpacity>
  )
}
