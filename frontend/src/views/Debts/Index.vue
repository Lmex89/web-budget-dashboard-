<script setup lang="ts">
import { ref } from 'vue'

const debts = ref([
  { id: '1', name: 'Car loan', type: 'we_owe', counterparty: 'Bank', original: 15000, remaining: 8200, status: 'active' },
  { id: '2', name: 'Mom loan', type: 'owed_to_us', counterparty: 'Mom', original: 2000, remaining: 500, status: 'active' },
])
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Debts</h1>
        <p class="text-base-content/60 text-sm">Track what you owe and what you're owed</p>
      </div>
      <button class="btn btn-primary">+ Add debt</button>
    </div>

    <div class="overflow-x-auto">
      <table class="table table-zebra">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Counterparty</th>
            <th>Original</th>
            <th>Remaining</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="debt in debts" :key="debt.id">
            <td class="font-medium">{{ debt.name }}</td>
            <td>
              <span class="badge" :class="debt.type === 'we_owe' ? 'badge-warning' : 'badge-info'">
                {{ debt.type === 'we_owe' ? 'We owe' : 'Owed to us' }}
              </span>
            </td>
            <td>{{ debt.counterparty }}</td>
            <td>${{ debt.original.toFixed(2) }}</td>
            <td class="font-semibold">${{ debt.remaining.toFixed(2) }}</td>
            <td>
              <span class="badge" :class="debt.status === 'paid' ? 'badge-success' : 'badge-ghost'">
                {{ debt.status }}
              </span>
            </td>
          </tr>
          <tr v-if="debts.length === 0">
            <td colspan="6" class="text-center text-base-content/40 py-8">No debts recorded</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
