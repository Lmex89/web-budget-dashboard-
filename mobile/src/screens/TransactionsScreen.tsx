import { useCallback, useMemo } from "react"
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { SearchBar } from "@/components/ui/SearchBar"
import { FilterChip } from "@/components/ui/FilterChip"
import { EmptyState } from "@/components/ui/EmptyState"
import { Card } from "@/components/ui/Card"
import { useTransactions } from "@/hooks/useTransactions"
import { useCategories } from "@/hooks/useCategories"
import { useFilterStore } from "@/stores/useFilterStore"
import { formatCurrency, formatDate } from "@/utils/format"
import { cn } from "@/utils/cn"
import type { Transaction } from "@/types"

export function TransactionsScreen() {
  const insets = useSafeAreaInsets()
  const filters = useFilterStore((s) => s.filters)
  const setSearch = useFilterStore((s) => s.setSearch)
  const setCategoryFilter = useFilterStore((s) => s.setCategoryFilter)
  const setTypeFilter = useFilterStore((s) => s.setTypeFilter)
  const clearFilters = useFilterStore((s) => s.clearFilters)

  const { data: transactions, isLoading, isError } = useTransactions()
  const { data: categories } = useCategories()

  const hasActiveFilters = useMemo(
    () => filters.search !== "" || !!filters.category_id || !!filters.type,
    [filters],
  )

  const handleSearch = useCallback(
    (text: string) => setSearch(text),
    [setSearch],
  )

  const renderItem = useCallback(
    ({ item }: { item: Transaction }) => (
      <View
        className="flex-row items-center py-3.5 px-1 border-b border-border/50 dark:border-border-dark/50"
        accessibilityLabel={`${item.description}, ${formatCurrency(item.amount)}`}
      >
        <View className="w-11 h-11 rounded-xl items-center justify-center bg-card dark:bg-card-dark">
          <Text className="text-xl">{item.category_icon || "💳"}</Text>
        </View>

        <View className="flex-1 ml-3">
          <Text className="text-[15px] font-medium text-ink dark:text-ink-dark" numberOfLines={1}>
            {item.description || item.category_name}
          </Text>
          <Text className="text-xs text-muted dark:text-muted mt-0.5">
            {formatDate(item.date)} · {item.category_name}
          </Text>
        </View>

        <Text
          className={cn(
            "text-[15px] font-semibold tabular-nums",
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
    <View className="flex-1 bg-surface dark:bg-surface-dark">
      <FlatList
        data={transactions ?? []}
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
              Transactions
            </Text>

            <SearchBar onSearch={handleSearch} className="mb-3" />

            <ScrollableFilters
              categories={categories ?? []}
              selectedCategoryId={filters.category_id}
              selectedType={filters.type}
              onCategoryPress={setCategoryFilter}
              onTypePress={setTypeFilter}
            />

            {hasActiveFilters && (
              <TouchableOpacity onPress={clearFilters} className="mb-3 self-start">
                <Text className="text-sm font-medium text-accent-blue">
                  Clear all filters
                </Text>
              </TouchableOpacity>
            )}
          </View>
        }
        ListEmptyComponent={
          isLoading ? (
            <View className="py-12 items-center">
              <ActivityIndicator size="large" className="text-accent-blue" />
            </View>
          ) : isError ? (
            <Card className="p-5 mt-4">
              <Text className="text-sm text-accent-red">Failed to load transactions</Text>
            </Card>
          ) : (
            <EmptyState
              icon="📭"
              title="No transactions found"
              description={hasActiveFilters ? "Try adjusting your filters" : "Add your first transaction to get started"}
            />
          )
        }
      />
    </View>
  )
}

function ScrollableFilters({
  categories,
  selectedCategoryId,
  selectedType,
  onCategoryPress,
  onTypePress,
}: {
  categories: { id: string; name: string; icon: string }[]
  selectedCategoryId?: string
  selectedType?: "income" | "expense"
  onCategoryPress: (id?: string) => void
  onTypePress: (type?: "income" | "expense") => void
}) {
  return (
    <View className="mb-4">
      <View className="flex-row gap-2 mb-2">
        <FilterChip
          label="All"
          selected={!selectedType}
          onPress={() => onTypePress(undefined)}
        />
        <FilterChip
          label="Income"
          selected={selectedType === "income"}
          onPress={() => onTypePress("income")}
        />
        <FilterChip
          label="Expenses"
          selected={selectedType === "expense"}
          onPress={() => onTypePress("expense")}
        />
      </View>
      <FlatList
        horizontal
        showsHorizontalScrollIndicator={false}
        data={categories}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ gap: 8 }}
        renderItem={({ item }) => (
          <FilterChip
            label={`${item.icon} ${item.name}`}
            selected={selectedCategoryId === item.id}
            onPress={() =>
              onCategoryPress(selectedCategoryId === item.id ? undefined : item.id)
            }
          />
        )}
      />
    </View>
  )
}
