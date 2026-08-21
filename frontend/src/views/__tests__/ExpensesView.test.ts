import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia, type Pinia } from 'pinia'
import { mount } from '@vue/test-utils'
import ExpensesView from '@/views/Expenses/Index.vue'
import { useExpenseStore } from '@/stores/expenses'
import { useCategoryStore } from '@/stores/categories'
import { useCreditCardStore } from '@/stores/creditCards'
import type { ExpenseListItem } from '@/types'

vi.mock('vue-router', () => ({
  useRoute: () => ({
    query: {},
  }),
}))

const mockExpenses: ExpenseListItem[] = [
  {
    id: 'exp-1',
    amount: '45.50',
    description: 'Weekly Groceries',
    date: '2026-08-20T12:00:00Z',
    payment_method: 'debit',
    category_id: 'cat-1',
    category_name: 'Food',
    credit_card_id: null,
    user_name: 'Alice',
    created_at: '2026-08-20T12:00:00Z',
  },
  {
    id: 'exp-2',
    amount: '12.00',
    description: 'Coffee',
    date: '2026-08-21T08:30:00Z',
    payment_method: 'cash',
    category_id: 'cat-2',
    category_name: 'Dining',
    credit_card_id: null,
    user_name: 'Bob',
    created_at: '2026-08-21T08:30:00Z',
  },
]

vi.mock('@/services/api', () => ({
  default: {
    get: vi.fn().mockImplementation((url: string) => {
      if (url === '/api/v1/expenses') {
        return Promise.resolve({
          data: {
            success: true,
            data: mockExpenses,
            total: mockExpenses.length,
            page: 1,
            total_pages: 1,
          },
        })
      }
      return Promise.resolve({ data: { success: true, data: [] } })
    }),
    delete: vi.fn().mockResolvedValue({ data: { success: true } }),
    post: vi.fn().mockResolvedValue({ data: { success: true } }),
    put: vi.fn().mockResolvedValue({ data: { success: true } }),
  },
}))

let pinia: Pinia

beforeEach(() => {
  pinia = createPinia()
  setActivePinia(pinia)
  vi.clearAllMocks()
  window.HTMLElement.prototype.scrollIntoView = vi.fn()
})

describe('ExpensesView delete confirmation and edit focus', () => {
  it('shows confirm and cancel buttons upon clicking delete before deleting', async () => {
    const expenseStore = useExpenseStore()
    const categoryStore = useCategoryStore()
    const creditCardStore = useCreditCardStore()

    categoryStore.categories = []
    creditCardStore.creditCards = []
    expenseStore.expenses = [...mockExpenses]
    expenseStore.total = 2
    expenseStore.totalPages = 1

    const deleteSpy = vi.spyOn(expenseStore, 'deleteExpense').mockResolvedValue({ success: true } as never)

    const wrapper = mount(ExpensesView, {
      global: {
        plugins: [pinia],
        stubs: {
          PageHeader: true,
          PaperCard: false,
          CategoryFilter: true,
          FormField: true,
          EmptyState: true,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 50))
    await wrapper.vm.$nextTick()

    // Find delete buttons in desktop table
    const tableRows = wrapper.findAll('tbody tr')
    expect(tableRows.length).toBe(2)

    const firstRowDeleteBtn = tableRows[0].find('button.text-danger')
    expect(firstRowDeleteBtn.exists()).toBe(true)
    expect(firstRowDeleteBtn.text()).toBe('Delete')

    // Click Delete on first expense
    await firstRowDeleteBtn.trigger('click')

    // Expect backend delete has NOT been called yet
    expect(deleteSpy).not.toHaveBeenCalled()

    // Confirm button and Cancel button should now be visible in first row
    const confirmBtn = tableRows[0].findAll('button').find((b) => b.text().includes('Confirm'))
    const cancelBtn = tableRows[0].findAll('button').find((b) => b.text().includes('Cancel'))

    expect(confirmBtn?.exists()).toBe(true)
    expect(cancelBtn?.exists()).toBe(true)

    // Click Cancel - should return to Delete button without calling backend
    await cancelBtn?.trigger('click')
    expect(deleteSpy).not.toHaveBeenCalled()

    const restoredDeleteBtn = tableRows[0].find('button.text-danger')
    expect(restoredDeleteBtn.text()).toBe('Delete')

    // Click Delete again, then click Confirm
    await restoredDeleteBtn.trigger('click')
    const secondConfirmBtn = tableRows[0].findAll('button').find((b) => b.text().includes('Confirm'))
    await secondConfirmBtn?.trigger('click')

    expect(deleteSpy).toHaveBeenCalledWith('exp-1')
  })

  it('handles mobile card delete confirmation and cancellation', async () => {
    const expenseStore = useExpenseStore()
    const categoryStore = useCategoryStore()
    const creditCardStore = useCreditCardStore()

    categoryStore.categories = []
    creditCardStore.creditCards = []
    expenseStore.expenses = [...mockExpenses]
    expenseStore.total = 2
    expenseStore.totalPages = 1

    const deleteSpy = vi.spyOn(expenseStore, 'deleteExpense').mockResolvedValue({ success: true } as never)

    const wrapper = mount(ExpensesView, {
      global: {
        plugins: [pinia],
        stubs: {
          PageHeader: true,
          PaperCard: false,
          CategoryFilter: true,
          FormField: true,
          EmptyState: true,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 50))
    await wrapper.vm.$nextTick()

    // Find mobile cards
    const mobileCards = wrapper.findAll('.md\\:hidden > div')
    expect(mobileCards.length).toBe(2)

    const mobileDeleteBtn = mobileCards[0].find('button.text-danger')
    expect(mobileDeleteBtn.text()).toBe('Delete')

    await mobileDeleteBtn.trigger('click')
    expect(deleteSpy).not.toHaveBeenCalled()

    const confirmBtn = mobileCards[0].findAll('button').find((b) => b.text().includes('Confirm'))
    const cancelBtn = mobileCards[0].findAll('button').find((b) => b.text().includes('Cancel'))
    expect(confirmBtn?.exists()).toBe(true)
    expect(cancelBtn?.exists()).toBe(true)

    await cancelBtn?.trigger('click')
    expect(deleteSpy).not.toHaveBeenCalled()
    expect(mobileCards[0].find('button.text-danger').text()).toBe('Delete')

    await mobileCards[0].find('button.text-danger').trigger('click')
    const secondConfirmBtn = mobileCards[0].findAll('button').find((b) => b.text().includes('Confirm'))
    await secondConfirmBtn?.trigger('click')

    expect(deleteSpy).toHaveBeenCalledWith('exp-1')
  })

  it('opens form, displays edit mode, and highlights row when Edit is clicked', async () => {
    const expenseStore = useExpenseStore()
    const categoryStore = useCategoryStore()
    const creditCardStore = useCreditCardStore()

    categoryStore.categories = []
    creditCardStore.creditCards = []
    expenseStore.expenses = [...mockExpenses]
    expenseStore.total = 2
    expenseStore.totalPages = 1

    const wrapper = mount(ExpensesView, {
      attachTo: document.body,
      global: {
        plugins: [pinia],
        stubs: {
          PageHeader: true,
          PaperCard: false,
          CategoryFilter: true,
          FormField: false,
          EmptyState: true,
        },
      },
    })

    await wrapper.vm.$nextTick()
    await new Promise((r) => setTimeout(r, 50))
    await wrapper.vm.$nextTick()

    // Find first row edit button
    const firstRow = wrapper.findAll('tbody tr')[0]
    const editBtn = firstRow.findAll('button').find((b) => b.text() === 'Edit')
    expect(editBtn?.exists()).toBe(true)

    await editBtn?.trigger('click')
    await wrapper.vm.$nextTick()

    // Form should now be open
    const form = wrapper.find('form')
    expect(form.exists()).toBe(true)
    expect(form.text()).toContain('Edit expense')
    expect(form.text()).toContain('Editing expense')

    // The amount input should have the value of 45.5
    const amountInput = form.find<HTMLInputElement>('input#amount')
    expect(amountInput.element.value).toBe('45.5')

    // The row should have editing highlight
    const updatedFirstRow = wrapper.findAll('tbody tr')[0]
    expect(updatedFirstRow.classes()).toContain('bg-accent-light/40')
    expect(updatedFirstRow.text()).toContain('Editing')

    // Cancel edit
    const formCancelBtn = form.findAll('button').find((b) => b.text() === 'Cancel')
    await formCancelBtn?.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.find('form').exists()).toBe(false)
  })
})
