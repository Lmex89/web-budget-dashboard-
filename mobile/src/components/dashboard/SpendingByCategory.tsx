import { View, Text, ActivityIndicator } from "react-native"
import { Card } from "@/components/ui/Card"
import { ProgressBar } from "@/components/ui/ProgressBar"
import { useBudget } from "@/hooks/useBudget"
import { formatCurrency, getPercentage } from "@/utils/format"
import { getCategoryColor } from "@/utils/colors"

export function SpendingByCategory() {
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
        <Text className="text-sm text-accent-red">Failed to load categories</Text>
      </Card>
    )
  }

  const sorted = [...budget.categories].sort((a, b) => b.spent - a.spent)

  return (
    <Card className="p-5">
      <Text className="text-sm font-medium text-muted dark:text-muted uppercase tracking-wide">
        Spending by Category
      </Text>

      <View className="mt-4 space-y-4">
        {sorted.map((cat) => {
          const pct = getPercentage(cat.spent, cat.budgeted)
          const color = getCategoryColor(cat.category_color)

          return (
            <View key={cat.category_id} className="space-y-1.5">
              <View className="flex-row justify-between items-center">
                <View className="flex-row items-center shrink">
                  <Text className="mr-2">{cat.category_icon}</Text>
                  <Text className="text-sm font-medium text-ink dark:text-ink-dark" numberOfLines={1}>
                    {cat.category_name}
                  </Text>
                </View>
                <Text className="text-sm font-semibold text-ink dark:text-ink-dark tabular-nums">
                  {formatCurrency(cat.spent)}
                </Text>
              </View>

              <ProgressBar
                value={cat.spent}
                max={cat.budgeted}
                color={color}
                barClassName="opacity-80"
              />

              <View className="flex-row justify-between">
                <Text className="text-xs text-muted dark:text-muted">
                  {pct}% of {formatCurrency(cat.budgeted)}
                </Text>
                {cat.spent > cat.budgeted && (
                  <Text className="text-xs font-medium text-accent-red">
                    {formatCurrency(cat.spent - cat.budgeted)} over
                  </Text>
                )}
              </View>
            </View>
          )
        })}
      </View>
    </Card>
  )
}
