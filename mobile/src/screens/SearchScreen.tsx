import { useCallback, useMemo, useState } from "react"
import {
  View,
  Text,
  FlatList,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
} from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { SearchBar } from "@/components/ui/SearchBar"
import { Card } from "@/components/ui/Card"
import { EmptyState } from "@/components/ui/EmptyState"
import { useTransactions } from "@/hooks/useTransactions"
import { formatCurrency, formatDate } from "@/utils/format"
import { cn } from "@/utils/cn"
import type { Transaction } from "@/types"

export function SearchScreen() {
  const insets = useSafeAreaInsets()
  const [query, setQuery] = useState("")
  const { data: transactions, isLoading } = useTransactions()

  const results = useMemo(() => {
    if (!query.trim() || !transactions) return []
    const lower = query.toLowerCase()
    return transactions.filter(
      (t: { description?: string; category_name?: string; amount: number }) =>
        t.description?.toLowerCase().includes(lower) ||
        t.category_name?.toLowerCase().includes(lower) ||
        t.amount.toString().includes(lower),
    )
  }, [query, transactions])

  const handleSearch = useCallback((text: string) => {
    setQuery(text)
  }, [])

  const renderItem = useCallback(
    ({ item }: { item: Transaction }) => (
      <View
        className="flex-row items-center py-3.5 px-1"
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
            {formatDate(item.date)} · {formatCurrency(item.amount)}
          </Text>
        </View>
        <Text
          className={cn(
            "text-sm font-semibold tabular-nums",
            item.type === "income" ? "text-accent-green" : "text-ink dark:text-ink-dark",
          )}
        >
          {item.type === "income" ? "+" : "-"}
          {formatCurrency(item.amount)}
        </Text>
      </View>
    ),
    [],
  )

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      className="flex-1 bg-surface dark:bg-surface-dark"
    >
      <FlatList
        data={results}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={{
          paddingTop: insets.top + 12,
          paddingBottom: insets.bottom + 24,
          paddingHorizontal: 16,
        }}
        ListHeaderComponent={
          <View>
            <Text className="text-2xl font-bold text-ink dark:text-ink-dark mb-5">
              Search
            </Text>
            <SearchBar
              onSearch={handleSearch}
              autoFocus
              className="mb-4"
            />
          </View>
        }
        ListEmptyComponent={
          query.trim() ? (
            <EmptyState
              icon="🔍"
              title="No results"
              description={`No transactions matching "${query}"`}
            />
          ) : (
            <EmptyState
              icon="🔎"
              title="Search transactions"
              description="Type a description, category, or amount to find transactions"
            />
          )
        }
      />
    </KeyboardAvoidingView>
  )
}
