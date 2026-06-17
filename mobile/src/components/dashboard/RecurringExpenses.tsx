import { View, Text, FlatList, ActivityIndicator } from "react-native"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { useRecurringExpenses } from "@/hooks/useRecurring"
import { formatCurrency, getRelativeDate } from "@/utils/format"
import { cn } from "@/utils/cn"

interface RecurringExpensesProps {
  limit?: number
}

export function RecurringExpenses({ limit = 4 }: RecurringExpensesProps) {
  const { data: recurring, isLoading, isError } = useRecurringExpenses()

  if (isLoading) {
    return (
      <Card className="p-5">
        <ActivityIndicator size="small" className="text-accent-blue" />
      </Card>
    )
  }

  if (isError) {
    return (
      <Card className="p-5">
        <Text className="text-sm text-accent-red">Failed to load recurring expenses</Text>
      </Card>
    )
  }

  const items = (recurring ?? [])
    .filter((r: { status: string }) => r.status === "active")
    .slice(0, limit)

  return (
    <Card className="p-5">
      <View className="flex-row justify-between items-center mb-4">
        <Text className="text-sm font-medium text-muted dark:text-muted uppercase tracking-wide">
          Recurring Expenses
        </Text>
        <Badge variant="info" label={`${(recurring ?? []).filter((r: { status: string }) => r.status === "active").length} active`} />
      </View>

      {items.length === 0 ? (
        <Text className="text-sm text-muted dark:text-muted text-center py-4">
          No recurring expenses
        </Text>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          scrollEnabled={false}
          renderItem={({ item }) => (
            <View
              className="flex-row items-center py-3 border-b border-border/50 dark:border-border-dark/50"
              accessibilityLabel={`${item.description}, ${formatCurrency(item.amount)}, ${item.frequency}`}
            >
              <View className="w-10 h-10 rounded-xl items-center justify-center bg-card dark:bg-card-dark">
                <Text className="text-lg">{item.category_icon || "🔄"}</Text>
              </View>

              <View className="flex-1 ml-3">
                <Text className="text-sm font-medium text-ink dark:text-ink-dark" numberOfLines={1}>
                  {item.description}
                </Text>
                <Text className="text-xs text-muted dark:text-muted mt-0.5 capitalize">
                  {item.frequency}
                </Text>
              </View>

              <View className="items-end">
                <Text className="text-sm font-semibold text-ink dark:text-ink-dark tabular-nums">
                  {formatCurrency(item.amount)}
                </Text>
                <Text
                  className={cn(
                    "text-xs mt-0.5",
                    item.next_due
                      ? "text-accent-orange"
                      : "text-muted dark:text-muted",
                  )}
                >
                  {item.next_due ? getRelativeDate(item.next_due) : "No due date"}
                </Text>
              </View>
            </View>
          )}
        />
      )}
    </Card>
  )
}
