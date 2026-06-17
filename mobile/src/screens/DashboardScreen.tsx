import { useCallback } from "react"
import { ScrollView, View, Text, TouchableOpacity } from "react-native"
import { useSafeAreaInsets } from "react-native-safe-area-context"
import { useThemeStore } from "@/stores/useThemeStore"
import { MonthlySpendingCard } from "@/components/dashboard/MonthlySpendingCard"
import { BudgetVsActual } from "@/components/dashboard/BudgetVsActual"
import { SpendingByCategory } from "@/components/dashboard/SpendingByCategory"
import { CashFlowChart } from "@/components/dashboard/CashFlowChart"
import { RecentTransactions } from "@/components/dashboard/RecentTransactions"
import { RecurringExpenses } from "@/components/dashboard/RecurringExpenses"

interface DashboardScreenProps {
  navigation?: {
    navigate: (screen: string) => void
  }
}

export function DashboardScreen({ navigation }: DashboardScreenProps) {
  const insets = useSafeAreaInsets()
  const toggleTheme = useThemeStore((s) => s.toggle)
  const isDark = useThemeStore((s) => s.isDark)

  const handleSeeAllTransactions = useCallback(() => {
    navigation?.navigate("Transactions")
  }, [navigation])

  return (
    <View className="flex-1 bg-surface dark:bg-surface-dark">
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingTop: insets.top + 12,
          paddingBottom: insets.bottom + 24,
          paddingHorizontal: 16,
        }}
      >
        {/* Header */}
        <View className="flex-row justify-between items-center mb-6">
          <View>
            <Text className="text-xs font-medium text-muted dark:text-muted uppercase tracking-wide">
              Welcome back
            </Text>
            <Text className="text-2xl font-bold text-ink dark:text-ink-dark mt-0.5">
              Dashboard
            </Text>
          </View>
          <TouchableOpacity
            onPress={toggleTheme}
            className="w-10 h-10 rounded-xl bg-card dark:bg-card-dark items-center justify-center"
            accessibilityLabel={isDark ? "Switch to light mode" : "Switch to dark mode"}
            accessibilityRole="button"
          >
            <Text className="text-lg">{isDark ? "☀️" : "🌙"}</Text>
          </TouchableOpacity>
        </View>

        {/* Monthly Spending */}
        <View className="mb-4">
          <MonthlySpendingCard />
        </View>

        {/* Budget vs Actual */}
        <View className="mb-4">
          <BudgetVsActual />
        </View>

        {/* Cash Flow Chart */}
        <View className="mb-4">
          <CashFlowChart />
        </View>

        {/* Spending by Category */}
        <View className="mb-4">
          <SpendingByCategory />
        </View>

        {/* Recent Transactions */}
        <View className="mb-4">
          <RecentTransactions onSeeAll={handleSeeAllTransactions} />
        </View>

        {/* Recurring Expenses */}
        <View className="mb-4">
          <RecurringExpenses />
        </View>
      </ScrollView>
    </View>
  )
}
