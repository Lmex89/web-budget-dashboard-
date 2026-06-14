<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useExpenseStore } from '@/stores/expenses'
import { useAuthStore } from '@/stores/auth'

const expenseStore = useExpenseStore()
const authStore = useAuthStore()

const currentMonth = ref(new Date().getMonth() + 1)
const currentYear = ref(new Date().getFullYear())

const summary = computed(() => expenseStore.monthlySummary)
const distribution = computed(() => expenseStore.categoryDistribution)

onMounted(async () => {
  await Promise.all([
    expenseStore.fetchMonthlySummary(currentYear.value, currentMonth.value),
    expenseStore.fetchCategoryDistribution(currentYear.value, currentMonth.value),
    expenseStore.fetchExpenses({ page_size: 5 }),
  ])
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Dashboard</h1>
        <p class="text-base-content/60 text-sm">
          Welcome back, {{ authStore.user?.full_name }}
        </p>
      </div>
      <div class="flex gap-2">
        <select v-model="currentMonth" class="select select-bordered select-sm">
          <option v-for="m in 12" :key="m" :value="m">{{ new Date(2000, m - 1).toLocaleString('default', { month: 'long' }) }}</option>
        </select>
        <select v-model="currentYear" class="select select-bordered select-sm">
          <option v-for="y in 5" :key="y" :value="currentYear - y + 1">{{ currentYear - y + 1 }}</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="stat bg-base-100 rounded-box shadow-sm">
        <div class="stat-title">Total expenses</div>
        <div class="stat-value text-primary">${{ summary?.total_expenses?.toFixed(2) || '0.00' }}</div>
        <div class="stat-desc">{{ new Date(currentYear, currentMonth - 1).toLocaleString('default', { month: 'long', year: 'numeric' }) }}</div>
      </div>
      <div class="stat bg-base-100 rounded-box shadow-sm">
        <div class="stat-title">Categories used</div>
        <div class="stat-value text-secondary">{{ distribution?.length || 0 }}</div>
        <div class="stat-desc">This month</div>
      </div>
      <div class="stat bg-base-100 rounded-box shadow-sm">
        <div class="stat-title">Family members</div>
        <div class="stat-value text-accent">1</div>
        <div class="stat-desc">Active</div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Category distribution placeholder -->
      <div class="card bg-base-100 shadow-sm">
        <div class="card-body">
          <h2 class="card-title text-sm">Category distribution</h2>
          <div v-if="distribution && distribution.length > 0" class="mt-4 space-y-3">
            <div v-for="cat in distribution" :key="cat.category" class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: cat.color || '#888' }"></div>
                <span class="text-sm">{{ cat.category }}</span>
              </div>
              <span class="text-sm font-semibold">${{ cat.amount.toFixed(2) }}</span>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center py-10 text-base-content/40">
            <p class="text-lg mb-2">📊</p>
            <p class="text-sm">No expenses this month</p>
          </div>
        </div>
      </div>

      <!-- Recent expenses -->
      <div class="card bg-base-100 shadow-sm">
        <div class="card-body">
          <h2 class="card-title text-sm">Recent expenses</h2>
          <div v-if="expenseStore.expenses.length > 0" class="mt-4 space-y-3">
            <div v-for="expense in expenseStore.expenses" :key="expense.id" class="flex items-center justify-between py-2 border-b border-base-200 last:border-0">
              <div>
                <p class="text-sm font-medium">{{ expense.description || expense.category_name }}</p>
                <p class="text-xs text-base-content/50">{{ expense.user_name }} · {{ new Date(expense.date).toLocaleDateString() }}</p>
              </div>
              <span class="text-sm font-semibold">${{ parseFloat(expense.amount).toFixed(2) }}</span>
            </div>
          </div>
          <div v-else class="flex flex-col items-center justify-center py-10 text-base-content/40">
            <p class="text-lg mb-2">💰</p>
            <p class="text-sm">No expenses yet</p>
            <router-link to="/expenses" class="btn btn-ghost btn-sm mt-2">Add one</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="flex gap-3">
      <router-link to="/expenses" class="btn btn-primary">
        + New expense
      </router-link>
      <router-link to="/categories" class="btn btn-outline">
        Manage categories
      </router-link>
    </div>
  </div>
</template>
