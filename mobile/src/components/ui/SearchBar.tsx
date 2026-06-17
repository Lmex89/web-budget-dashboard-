import { useState, useCallback, useRef } from "react"
import {
  View,
  TextInput,
  TouchableOpacity,
  Text,
  type TextInputProps,
} from "react-native"
import { cn } from "@/utils/cn"

interface SearchBarProps extends Omit<TextInputProps, "onChangeText"> {
  onSearch: (text: string) => void
  placeholder?: string
}

export function SearchBar({
  onSearch,
  placeholder = "Search transactions…",
  className,
  ...inputProps
}: SearchBarProps) {
  const [value, setValue] = useState("")
  const inputRef = useRef<TextInput>(null)

  const handleChange = useCallback(
    (text: string) => {
      setValue(text)
      onSearch(text)
    },
    [onSearch],
  )

  const handleClear = useCallback(() => {
    setValue("")
    onSearch("")
    inputRef.current?.focus()
  }, [onSearch])

  return (
    <View
      className={cn(
        "flex-row items-center rounded-xl bg-card px-3 py-2 dark:bg-card-dark",
        className,
      )}
    >
      <Text className="text-muted dark:text-muted mr-2 text-base">🔍</Text>
      <TextInput
        ref={inputRef}
        value={value}
        onChangeText={handleChange}
        placeholder={placeholder}
        placeholderTextColor="#8e8e93"
        className="flex-1 text-base text-ink dark:text-ink-dark"
        returnKeyType="search"
        accessibilityLabel="Search transactions"
        {...inputProps}
      />
      {value.length > 0 && (
        <TouchableOpacity
          onPress={handleClear}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          accessibilityLabel="Clear search"
          accessibilityRole="button"
        >
          <Text className="text-muted dark:text-muted text-base">✕</Text>
        </TouchableOpacity>
      )}
    </View>
  )
}
