import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native"
import { Card } from "@/components/ui/Card"
import { useTransactions } from "@/hooks/useTransactions"
import { formatCurrency, formatDate } from "@/utils/format"
import { cn } from "@/utils/cn"

interface RecentTransactionsProps {
  onSeeAll?: () => void
  limit?: number
}

export function RecentTransactions({
  onSeeAll,
  limit = 5,
}: RecentTransactionsProps) {
  const { data: transactions, isLoading, isError } = useTransactions()

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
        <Text className="text-sm text-accent-red">Failed to load transactions</Text>
      </Card>
    )
  }

  const items = (transactions ?? []).slice(0, limit)

  return (
    <Card className="p-5">
      <View className="flex-row justify-between items-center mb-4">
        <Text className="text-sm font-medium text-muted dark:text-muted uppercase tracking-wide">
          Recent Transactions
        </Text>
        {onSeeAll && items.length > 0 && (
          <TouchableOpacity
            onPress={onSeeAll}
            accessibilityLabel="See all transactions"
            accessibilityRole="button"
          >
            <Text className="text-sm font-medium text-accent-blue">See all</Text>
          </TouchableOpacity>
        )}
      </View>

      {items.length === 0 ? (
        <Text className="text-sm text-muted dark:text-muted text-center py-4">
          No transactions yet
        </Text>
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          scrollEnabled={false}
          renderItem={({ item }) => (
            <View
              className="flex-row items-center py-3 border-b border-border/50 dark:border-border-dark/50"
              accessibilityLabel={`${item.description}, ${formatCurrency(item.amount)}`}
            >
              <View className="w-10 h-10 rounded-xl items-center justify-center bg-card dark:bg-card-dark">
                <Text className="text-lg">{item.category_icon || "💳"}</Text>
              </View>

              <View className="flex-1 ml-3">
                <Text className="text-sm font-medium text-ink dark:text-ink-dark" numberOfLines={1}>
                  {item.description || item.category_name}
                </Text>
                <Text className="text-xs text-muted dark:text-muted mt-0.5">
                  {formatDate(item.date)} · {item.payment_method}
                </Text>
              </View>

              <Text
                className={cn(
                  "text-sm font-semibold tabular-nums",
                  item.type === "income"
                    ? "text-accent-green"
                    : "text-ink dark:text-ink-dark",
                )}
              >
                {item.type === "income" ? "+" : "-"}
                {formatCurrency(item.amount)}
              </Text>
            </View>
          )}
        />
      )}
    </Card>
  )
}
