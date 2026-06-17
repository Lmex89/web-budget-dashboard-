import { create } from "zustand"
import type { FilterState, TransactionFilters } from "@/types"

const defaultFilters: TransactionFilters = {
  search: "",
  sort_by: "date",
  sort_order: "desc",
}

export const useFilterStore = create<FilterState>((set) => ({
  filters: { ...defaultFilters },

  setSearch: (search: string) =>
    set((state) => ({ filters: { ...state.filters, search } })),

  setCategoryFilter: (category_id?: string) =>
    set((state) => ({ filters: { ...state.filters, category_id } })),

  setTypeFilter: (type?: "income" | "expense") =>
    set((state) => ({ filters: { ...state.filters, type } })),

  setDateRange: (start_date?: string, end_date?: string) =>
    set((state) => ({ filters: { ...state.filters, start_date, end_date } })),

  setSort: (sort_by, sort_order) =>
    set((state) => ({ filters: { ...state.filters, sort_by, sort_order } })),

  clearFilters: () => set({ filters: { ...defaultFilters } }),
}))
