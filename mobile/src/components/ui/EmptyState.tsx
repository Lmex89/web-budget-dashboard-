import { View, Text } from "react-native"

interface EmptyStateProps {
  icon?: string
  title: string
  description?: string
}

export function EmptyState({ icon = "📭", title, description }: EmptyStateProps) {
  return (
    <View className="items-center justify-center py-12 px-8">
      <Text className="text-4xl mb-4">{icon}</Text>
      <Text className="text-lg font-semibold text-ink dark:text-ink-dark text-center">
        {title}
      </Text>
      {description && (
        <Text className="text-sm text-muted dark:text-muted text-center mt-1 leading-5">
          {description}
        </Text>
      )}
    </View>
  )
}
