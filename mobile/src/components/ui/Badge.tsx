import { View, Text, type ViewProps } from "react-native"
import { cn } from "@/utils/cn"

interface BadgeProps extends ViewProps {
  variant?: "default" | "success" | "warning" | "danger" | "info"
  label: string
}

const variantStyles = {
  default: "bg-muted/15 text-muted dark:bg-muted/20 dark:text-muted",
  success: "bg-accent-green/15 text-accent-green",
  warning: "bg-accent-orange/15 text-accent-orange",
  danger: "bg-accent-red/15 text-accent-red",
  info: "bg-accent-blue/15 text-accent-blue",
}

export function Badge({ variant = "default", label, className, ...props }: BadgeProps) {
  return (
    <View
      className={cn(
        "self-start rounded-full px-2.5 py-1",
        variantStyles[variant].split(" ").slice(0, 2).join(" "),
        className,
      )}
      {...props}
    >
      <Text
        className={cn(
          "text-xs font-semibold",
          variantStyles[variant].split(" ").slice(2).join(" "),
        )}
      >
        {label}
      </Text>
    </View>
  )
}
