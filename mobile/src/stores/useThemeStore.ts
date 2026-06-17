import { create } from "zustand"
import { useColorScheme } from "react-native"
import type { ThemeMode, ThemeState } from "@/types"

function resolveIsDark(mode: ThemeMode): boolean {
  if (mode === "system") {
    return useColorScheme() === "dark"
  }
  return mode === "dark"
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  mode: "system",
  isDark: false,

  setMode: (mode: ThemeMode) => {
    set({ mode, isDark: resolveIsDark(mode) })
  },

  toggle: () => {
    const next = get().isDark ? "light" : "dark"
    set({ mode: next, isDark: next === "dark" })
  },
}))
