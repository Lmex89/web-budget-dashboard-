<script setup lang="ts">
import { ref } from 'vue'

const categories = ref([
  { id: '1', name: 'Food', color: '#f97316', icon: '🍕' },
  { id: '2', name: 'Transport', color: '#3b82f6', icon: '🚗' },
  { id: '3', name: 'Utilities', color: '#22c55e', icon: '💡' },
  { id: '4', name: 'Entertainment', color: '#a855f7', icon: '🎬' },
  { id: '5', name: 'Health', color: '#ef4444', icon: '🏥' },
])
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Categories</h1>
        <p class="text-base-content/60 text-sm">Organize expenses by category</p>
      </div>
      <button class="btn btn-primary">+ Add category</button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="cat in categories" :key="cat.id" class="card bg-base-100 shadow-sm">
        <div class="card-body flex flex-row items-center gap-4">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl" :style="{ backgroundColor: cat.color + '20' }">
            {{ cat.icon }}
          </div>
          <div>
            <h3 class="font-semibold">{{ cat.name }}</h3>
            <p class="text-xs text-base-content/50">{{ cat.color }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
