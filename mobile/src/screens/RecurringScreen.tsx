import { useCallback, useMemo } from "react"
import { View, Text, FlatList, ActivityIndicator, TouchableOpacity } from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { EmptyState } from "@/components/ui/EmptyState"
import { useRecurringExpenses } from "@/hooks/useRecurring"
import { formatCurrency, getRelativeDate } from "@/utils/format"
import { cn } from "@/utils/cn"
import type { RecurringExpense } from "@/types"

export function RecurringScreen() {
  const insets = useSafeAreaInsets()
  const { data: recurring, isLoading, isError } = useRecurringExpenses()

  const statusBadge = useCallback((status: RecurringExpense["status"]) => {
    switch (status) {
      case "active":
        return <Badge variant="success" label="Active" />
      case "paused":
        return <Badge variant="warning" label="Paused" />
      case "cancelled":
        return <Badge variant="danger" label="Cancelled" />
    }
  }, [])

  const renderItem = useCallback(
    ({ item }: { item: RecurringExpense }) => (
      <View
        className="p-4 mb-3 rounded-2xl bg-card dark:bg-card-dark"
        accessibilityLabel={`${item.description}, ${formatCurrency(item.amount)}, ${item.frequency}`}
      >
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center flex-1">
            <View className="w-11 h-11 rounded-xl items-center justify-center bg-surface dark:bg-surface-dark">
              <Text className="text-xl">{item.category_icon || "🔄"}</Text>
            </View>
            <View className="ml-3 flex-1">
              <Text className="text-[15px] font-medium text-ink dark:text-ink-dark">
                {item.description}
              </Text>
              <Text className="text-xs text-muted dark:text-muted mt-0.5 capitalize">
                {item.frequency} · {item.payment_method}
              </Text>
            </View>
          </View>
          {statusBadge(item.status)}
        </View>

        <View className="flex-row justify-between items-center mt-3 pt-3 border-t border-border/50 dark:border-border-dark/50">
          <View>
            <Text className="text-xs text-muted dark:text-muted">Next due</Text>
            <Text
              className={cn(
                "text-sm font-medium mt-0.5",
                item.status === "active" ? "text-ink dark:text-ink-dark" : "text-muted",
              )}
            >
              {item.next_due ? getRelativeDate(item.next_due) : "N/A"}
            </Text>
          </View>
          <Text className="text-lg font-bold text-ink dark:text-ink-dark tabular-nums">
            {formatCurrency(item.amount)}
          </Text>
        </View>
      </View>
    ),
    [statusBadge],
  )

  return (
    <View className="flex-1 bg-surface dark:bg-surface-dark">
      <FlatList
        data={recurring ?? []}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={{
          paddingTop: insets.top + 12,
          paddingBottom: insets.bottom + 24,
          paddingHorizontal: 16,
        }}
        ListHeaderComponent={
          <View className="flex-row justify-between items-center mb-5">
            <Text className="text-2xl font-bold text-ink dark:text-ink-dark">
              Recurring
            </Text>
          </View>
        }
        ListEmptyComponent={
          isLoading ? (
            <View className="py-12 items-center">
              <ActivityIndicator size="large" className="text-accent-blue" />
            </View>
          ) : isError ? (
            <Card className="p-5">
              <Text className="text-sm text-accent-red">Failed to load recurring expenses</Text>
            </Card>
          ) : (
            <EmptyState
              icon="🔄"
              title="No recurring expenses"
              description="Set up recurring expenses for subscriptions, rent, and regular bills"
            />
          )
        }
      />
    </View>
  )
}
