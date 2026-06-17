import { View, Text, ActivityIndicator } from "react-native"
import { Card } from "@/components/ui/Card"
import { useMonthlySpending } from "@/hooks/useAnalytics"
import { formatCurrency } from "@/utils/format"
import { cn } from "@/utils/cn"

export function MonthlySpendingCard() {
  const { data, isLoading, isError } = useMonthlySpending()

  if (isLoading) {
    return (
      <Card className="p-5">
        <ActivityIndicator size="small" className="text-accent-blue" />
      </Card>
    )
  }

  if (isError || !data) {
    return (
      <Card className="p-5">
        <Text className="text-sm text-accent-red">Failed to load spending</Text>
      </Card>
    )
  }

  const isDown = data.change_pct < 0
  const isUp = data.change_pct > 0

  return (
    <Card className="p-5">
      <Text className="text-sm font-medium text-muted dark:text-muted uppercase tracking-wide">
        Monthly Spending
      </Text>

      <Text
        className="text-3xl font-bold text-ink dark:text-ink-dark mt-1"
        accessibilityLabel={`Total spending ${formatCurrency(data.total)}`}
      >
        {formatCurrency(data.total)}
      </Text>

      <View className="flex-row items-center mt-2">
        <View
          className={cn(
            "rounded-full px-2 py-0.5",
            isDown && "bg-accent-green/15",
            isUp && "bg-accent-red/15",
            !isDown && !isUp && "bg-muted/15",
          )}
        >
          <Text
            className={cn(
              "text-xs font-semibold",
              isDown && "text-accent-green",
              isUp && "text-accent-red",
              !isDown && !isUp && "text-muted",
            )}
          >
            {isDown ? "↓" : isUp ? "↑" : "→"} {Math.abs(data.change_pct).toFixed(1)}%
          </Text>
        </View>
        <Text className="text-xs text-muted dark:text-muted ml-2">
          vs last month ({formatCurrency(data.previous_total)})
        </Text>
      </View>
    </Card>
  )
}
