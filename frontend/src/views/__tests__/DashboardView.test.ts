import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia, type Pinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { useExpenseStore } from '@/stores/expenses'
import { useCategoryStore } from '@/stores/categories'
import DashboardView from '@/views/DashboardView.vue'
import type { CategoryDistribution, Category } from '@/types'
import { CATEGORY_COLORS_LIGHT } from '@/utils/colors'

function makeDist(category: string, amount: number): CategoryDistribution {
  return { category, color: null, amount }
}

function makeCat(name: string, id?: string): Category {
  return {
    id: id || name.toLowerCase(),
    name,
    color: null,
    icon: null,
    family_id: 'f1',
    parent_id: null,
    created_at: '2024-01-01T00:00:00Z',
  }
}

let pinia: Pinia

beforeEach(() => {
  pinia = createPinia()
  setActivePinia(pinia)
})

describe('DashboardView color assignment', () => {
  it('assigns unique palette colors to segments', async () => {
    const expenseStore = useExpenseStore()
    const categoryStore = useCategoryStore()

    categoryStore.categories = [
      makeCat('Food', 'c1'),
      makeCat('Transport', 'c2'),
      makeCat('Entertainment', 'c3'),
    ]

    expenseStore.categoryDistribution = [
      makeDist('Food', 300),
      makeDist('Transport', 150),
      makeDist('Entertainment', 75),
    ]

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [pinia],
        stubs: {
          StatCard: true,
          CategoryStackedBar: true,
          RecentExpensesCard: true,
          TopCategoriesCard: true,
          ExpensesPieChart: {
            props: ['segments'],
            template: '<div><div v-for="s in segments" :key="s.categoryId" class="segment-dot" :data-color="s.color" :data-name="s.categoryName" /></div>',
          },
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 100))
    await wrapper.vm.$nextTick()

    const dots = wrapper.findAll('.segment-dot')
    expect(dots.length).toBeGreaterThanOrEqual(3)

    const colors = dots.map((d) => d.attributes('data-color'))
    const unique = new Set(colors)
    expect(unique.size).toBe(dots.length)
  })

  it('ignores DB color and always uses palette', async () => {
    const expenseStore = useExpenseStore()
    const categoryStore = useCategoryStore()

    categoryStore.categories = [
      makeCat('Food', 'c1'),
      makeCat('Transport', 'c2'),
    ]

    expenseStore.categoryDistribution = [
      { category: 'Food', color: '#0071e3', amount: 200 },
      { category: 'Transport', color: '#0071e3', amount: 100 },
    ]

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [pinia],
        stubs: {
          StatCard: true,
          CategoryStackedBar: true,
          RecentExpensesCard: true,
          TopCategoriesCard: true,
          ExpensesPieChart: {
            props: ['segments'],
            template: '<div><div v-for="s in segments" :key="s.categoryId" class="segment-dot" :data-color="s.color" :data-name="s.categoryName" /></div>',
          },
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 100))
    await wrapper.vm.$nextTick()

    const dots = wrapper.findAll('.segment-dot')
    expect(dots.length).toBe(2)

    const colors = dots.map((d) => d.attributes('data-color'))
    expect(colors[0]).toBe(CATEGORY_COLORS_LIGHT[0])
    expect(colors[1]).toBe(CATEGORY_COLORS_LIGHT[1])
    expect(colors[0]).not.toBe(colors[1])
  })

  it('shows all segments without grouping into Others', async () => {
    const expenseStore = useExpenseStore()
    const categoryStore = useCategoryStore()

    const names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    categoryStore.categories = names.map((n, i) => makeCat(n, `c${i}`))
    expenseStore.categoryDistribution = names.map((n, i) => makeDist(n, 100 * (7 - i)))

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [pinia],
        stubs: {
          StatCard: true,
          CategoryStackedBar: true,
          RecentExpensesCard: true,
          TopCategoriesCard: true,
          ExpensesPieChart: {
            props: ['segments'],
            template: '<div><div v-for="s in segments" :key="s.categoryId" class="segment-dot" :data-color="s.color" :data-name="s.categoryName" /></div>',
          },
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 100))
    await wrapper.vm.$nextTick()

    const dots = wrapper.findAll('.segment-dot')
    expect(dots.length).toBe(7)

    const colors = dots.map((d) => d.attributes('data-color'))
    const unique = new Set(colors)
    expect(unique.size).toBe(7)
  })

  it('stacked bar shows top 5 + Others when more than 6 categories', async () => {
    const expenseStore = useExpenseStore()
    const categoryStore = useCategoryStore()

    const names = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    categoryStore.categories = names.map((n, i) => makeCat(n, `c${i}`))
    expenseStore.categoryDistribution = names.map((n, i) => makeDist(n, 100 * (7 - i)))

    const wrapper = mount(DashboardView, {
      global: {
        plugins: [pinia],
        stubs: {
          StatCard: true,
          CategoryStackedBar: {
            props: ['segments'],
            template: '<div><div v-for="s in segments" :key="s.categoryId" class="bar-segment" :data-color="s.color" :data-name="s.categoryName" /></div>',
          },
          RecentExpensesCard: true,
          TopCategoriesCard: true,
          ExpensesPieChart: true,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 100))
    await wrapper.vm.$nextTick()

    const dots = wrapper.findAll('.bar-segment')
    expect(dots.length).toBe(6)

    const others = dots.find((d) => d.attributes('data-name') === 'Otros (2)')
    expect(others?.attributes('data-color')).toBe('#8e8e93')
  })
})
