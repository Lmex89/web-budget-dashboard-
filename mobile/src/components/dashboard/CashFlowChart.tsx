import { View, Text, ActivityIndicator, Dimensions } from "react-native"
import Svg, { Path, Line, Text as SvgText, Circle, G, Rect } from "react-native-svg"
import { Card } from "@/components/ui/Card"
import { useCashFlow } from "@/hooks/useAnalytics"
import { formatCompactCurrency } from "@/utils/format"
import { cn } from "@/utils/cn"

const CHART_HEIGHT = 180
const CHART_PADDING = { top: 16, right: 16, bottom: 28, left: 50 }

function generatePath(
  data: { value: number }[],
  width: number,
  height: number,
): string {
  if (data.length === 0) return ""
  const values = data.map((d) => d.value)
  const min = Math.min(...values, 0)
  const max = Math.max(...values)
  const range = max - min || 1

  const xStep = (width - CHART_PADDING.left - CHART_PADDING.right) / Math.max(data.length - 1, 1)
  const yScale = (val: number) =>
    height - CHART_PADDING.bottom - ((val - min) / range) * (height - CHART_PADDING.top - CHART_PADDING.bottom)

  return data
    .map((d, i) => {
      const x = CHART_PADDING.left + i * xStep
      const y = yScale(d.value)
      return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`
    })
    .join(" ")
}

function generateAreaPath(
  data: { value: number }[],
  width: number,
  height: number,
): string {
  if (data.length === 0) return ""
  const linePath = generatePath(data, width, height)
  const last = data.length - 1
  const xStep = (width - CHART_PADDING.left - CHART_PADDING.right) / Math.max(data.length - 1, 1)
  const lastX = CHART_PADDING.left + last * xStep
  const bottomY = height - CHART_PADDING.bottom

  return `${linePath} L ${lastX} ${bottomY} L ${CHART_PADDING.left} ${bottomY} Z`
}

export function CashFlowChart() {
  const { data, isLoading, isError } = useCashFlow()
  const screenWidth = Dimensions.get("window").width
  const chartWidth = screenWidth - 64

  if (isLoading) {
    return (
      <Card className="p-5">
        <ActivityIndicator size="small" className="text-accent-blue" />
      </Card>
    )
  }

  if (isError || !data || data.length === 0) {
    return (
      <Card className="p-5">
        <Text className="text-sm text-accent-red">Failed to load cash flow</Text>
      </Card>
    )
  }

  const incomeData = data.map((d: { income: number }) => ({ value: d.income }))
  const expenseData = data.map((d: { expense: number }) => ({ value: -d.expense }))
  const balanceData = data.map((d: { balance: number }) => ({ value: d.balance }))

  return (
    <Card className="p-5">
      <Text className="text-sm font-medium text-muted dark:text-muted uppercase tracking-wide">
        Cash Flow
      </Text>

      <View className="flex-row justify-between mt-3 mb-2">
        <View className="flex-row items-center">
          <View className="w-2.5 h-2.5 rounded-full bg-accent-green mr-1.5" />
          <Text className="text-xs text-muted dark:text-muted">Income</Text>
        </View>
        <View className="flex-row items-center">
          <View className="w-2.5 h-2.5 rounded-full bg-accent-red mr-1.5" />
          <Text className="text-xs text-muted dark:text-muted">Expenses</Text>
        </View>
        <View className="flex-row items-center">
          <View className="w-2.5 h-2.5 rounded-full bg-accent-blue mr-1.5" />
          <Text className="text-xs text-muted dark:text-muted">Balance</Text>
        </View>
      </View>

      <Svg width={chartWidth} height={CHART_HEIGHT} accessibilityLabel="Cash flow chart">
        <G>
          {incomeData.length > 1 && (
            <>
              <Path
                d={generateAreaPath(incomeData, chartWidth, CHART_HEIGHT)}
                fill="rgba(52, 199, 89, 0.08)"
              />
              <Path
                d={generatePath(incomeData, chartWidth, CHART_HEIGHT)}
                stroke="#34c759"
                strokeWidth={2}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </>
          )}

          {expenseData.length > 1 && (
            <>
              <Path
                d={generateAreaPath(expenseData, chartWidth, CHART_HEIGHT)}
                fill="rgba(255, 59, 48, 0.06)"
              />
              <Path
                d={generatePath(expenseData, chartWidth, CHART_HEIGHT)}
                stroke="#ff3b30"
                strokeWidth={2}
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </>
          )}

          {balanceData.length > 1 && (
            <Path
              d={generatePath(balanceData, chartWidth, CHART_HEIGHT)}
              stroke="#007aff"
              strokeWidth={2.5}
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )}
        </G>

        {[0, data.length - 1].map((i) => (
          <SvgText
            key={i}
            x={CHART_PADDING.left + i * ((chartWidth - CHART_PADDING.left - CHART_PADDING.right) / Math.max(data.length - 1, 1))}
            y={CHART_HEIGHT - 6}
            fill="#8e8e93"
            fontSize={10}
            textAnchor={i === 0 ? "start" : "end"}
          >
            {new Date(data[i].date).toLocaleDateString("en-US", { month: "short" })}
          </SvgText>
        ))}
      </Svg>
    </Card>
  )
}
