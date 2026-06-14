<script setup lang="ts">
import { ref } from 'vue'

const cards = ref([
  { id: '1', name: 'Visa Platinum', last_four: '4532', limit: 5000, balance: 1230.50, closing_day: 15, due_day: 5 },
  { id: '2', name: 'Mastercard Gold', last_four: '8876', limit: 3000, balance: 890.00, closing_day: 10, due_day: 28 },
])
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Credit cards</h1>
        <p class="text-base-content/60 text-sm">Track limits, balances, and due dates</p>
      </div>
      <button class="btn btn-primary">+ Add card</button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div v-for="card in cards" :key="card.id" class="card bg-base-100 shadow-sm">
        <div class="card-body">
          <div class="flex justify-between items-start">
            <div>
              <h2 class="card-title text-lg">{{ card.name }}</h2>
              <p class="text-sm text-base-content/50">•••• {{ card.last_four }}</p>
            </div>
            <div class="badge badge-outline">{{ (card.balance / card.limit * 100).toFixed(0) }}% used</div>
          </div>
          <div class="mt-4 space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Limit</span>
              <span class="font-semibold">${{ card.limit.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Balance</span>
              <span class="font-semibold">${{ card.balance.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Closing day</span>
              <span>{{ card.closing_day }}th</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-base-content/60">Due day</span>
              <span>{{ card.due_day }}th</span>
            </div>
          </div>
          <div class="w-full bg-base-200 rounded-full h-2 mt-3">
            <div class="bg-primary h-2 rounded-full transition-all" :style="{ width: (card.balance / card.limit * 100) + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
