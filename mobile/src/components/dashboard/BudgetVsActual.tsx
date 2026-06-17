import { View, Text, ActivityIndicator } from "react-native"
import { Card } from "@/components/ui/Card"
import { ProgressBar } from "@/components/ui/ProgressBar"
import { useBudget } from "@/hooks/useBudget"
import { formatCurrency, getPercentage } from "@/utils/format"
import { cn } from "@/utils/cn"

export function BudgetVsActual() {
  const { data: budget, isLoading, isError } = useBudget()

  if (isLoading) {
    return (
      <Card className="p-5">
        <ActivityIndicator size="small" className="text-accent-blue" />
      </Card>
    )
  }

  if (isError || !budget) {
    return (
      <Card className="p-5">
        <Text className="text-sm text-accent-red">Failed to load budget</Text>
      </Card>
    )
  }

  const pct = getPercentage(budget.total_spent, budget.total_budgeted)
  const isOver = budget.total_spent > budget.total_budgeted
  const remaining = budget.total_budgeted - budget.total_spent

  return (
    <Card className="p-5">
      <Text className="text-sm font-medium text-muted dark:text-muted uppercase tracking-wide">
        Budget vs Actual
      </Text>

      <View className="flex-row justify-between items-baseline mt-3">
        <Text className="text-2xl font-bold text-ink dark:text-ink-dark">
          {formatCurrency(budget.total_spent)}
        </Text>
        <Text className="text-sm text-muted dark:text-muted">
          of {formatCurrency(budget.total_budgeted)}
        </Text>
      </View>

      <ProgressBar
        value={budget.total_spent}
        max={budget.total_budgeted}
        className="mt-3"
        barClassName={cn(isOver ? "bg-accent-red" : "bg-accent-green")}
      />

      <Text
        className={cn(
          "text-xs font-medium mt-2",
          isOver ? "text-accent-red" : "text-accent-green",
        )}
      >
        {isOver
          ? `${formatCurrency(Math.abs(remaining))} over budget`
          : `${formatCurrency(remaining)} remaining`}
        {" · "}
        {pct}% used
      </Text>
    </Card>
  )
}
