import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RecentExpensesCard from '@/components/dashboard/RecentExpensesCard.vue'
import type { DashboardExpense } from '@/types'

const mockExpenses: DashboardExpense[] = [
  {
    id: 'exp-1',
    description: 'Groceries',
    amount: 54.2,
    date: '2026-08-20',
    categoryId: 'c1',
    authorName: 'Alex',
  },
]

describe('RecentExpensesCard delete confirmation', () => {
  it('shows confirm and cancel buttons when delete is clicked before emitting delete', async () => {
    const wrapper = mount(RecentExpensesCard, {
      props: {
        expenses: mockExpenses,
      },
      global: {
        stubs: {
          'router-link': true,
          PaperCard: false,
          EmptyState: true,
        },
      },
    })

    const deleteBtn = wrapper.find('button.text-danger')
    expect(deleteBtn.text()).toBe('Delete')

    await deleteBtn.trigger('click')

    // Expect delete event was NOT emitted yet
    expect(wrapper.emitted('delete')).toBeUndefined()

    // Confirm & Cancel buttons are shown
    const confirmBtn = wrapper.findAll('button').find((b) => b.text() === 'Confirm')
    const cancelBtn = wrapper.findAll('button').find((b) => b.text() === 'Cancel')

    expect(confirmBtn?.exists()).toBe(true)
    expect(cancelBtn?.exists()).toBe(true)

    // Click cancel
    await cancelBtn?.trigger('click')
    expect(wrapper.emitted('delete')).toBeUndefined()
    expect(wrapper.find('button.text-danger').text()).toBe('Delete')

    // Click delete again and then confirm
    await wrapper.find('button.text-danger').trigger('click')
    const secondConfirmBtn = wrapper.findAll('button').find((b) => b.text() === 'Confirm')
    await secondConfirmBtn?.trigger('click')

    expect(wrapper.emitted('delete')).toBeTruthy()
    expect(wrapper.emitted('delete')?.[0]).toEqual(['exp-1'])
  })
})
