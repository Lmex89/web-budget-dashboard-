import { useQuery } from "@tanstack/react-query"
import { api } from "@/services/api"

const CATEGORIES_KEY = ["categories"] as const

export function useCategories() {
  return useQuery({
    queryKey: CATEGORIES_KEY,
    queryFn: () => api.categories.list(),
  })
}

export function useCategory(id: string) {
  const { data: categories } = useCategories()

  return categories?.find((c: { id: string }) => c.id === id)
}
