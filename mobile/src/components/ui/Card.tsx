import { View, type ViewProps } from "react-native"
import { cn } from "@/utils/cn"

interface CardProps extends ViewProps {
  variant?: "default" | "elevated" | "filled"
}

export function Card({
  variant = "default",
  className,
  children,
  ...props
}: CardProps) {
  return (
    <View
      className={cn(
        "rounded-2xl p-4",
        variant === "default" && "bg-card dark:bg-card-dark",
        variant === "elevated" && "bg-elevated dark:bg-elevated-dark shadow-sm",
        variant === "filled" && "bg-card dark:bg-card-dark",
        className,
      )}
      {...props}
    >
      {children}
    </View>
  )
}
