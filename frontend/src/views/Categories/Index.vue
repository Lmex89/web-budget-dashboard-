<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useCategoryStore } from '@/stores/categories'

const categoryStore = useCategoryStore()
const showForm = ref(false)
const errorMessage = ref('')

const form = ref({
  name: '',
  color: '#3b82f6',
  icon: '',
})

onMounted(async () => {
  await categoryStore.fetchCategories()
})

async function handleCreate() {
  errorMessage.value = ''
  try {
    await categoryStore.createCategory({
      name: form.value.name.trim(),
      color: form.value.color || null,
      icon: form.value.icon.trim() || null,
    })
    showForm.value = false
    form.value = { name: '', color: '#3b82f6', icon: '' }
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.error?.message || 'Failed to create category'
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Categories</h1>
        <p class="text-base-content/60 text-sm">Organize expenses by category</p>
      </div>
      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Add category' }}
      </button>
    </div>

    <form v-if="showForm" @submit.prevent="handleCreate" class="card bg-base-100 shadow-sm p-6 space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="form-control md:col-span-2">
          <label class="label"><span class="label-text">Name</span></label>
          <input v-model="form.name" type="text" class="input input-bordered" maxlength="100" required />
        </div>
        <div class="form-control">
          <label class="label"><span class="label-text">Color</span></label>
          <input v-model="form.color" type="color" class="input input-bordered h-12 p-1" />
        </div>
        <div class="form-control md:col-span-3">
          <label class="label"><span class="label-text">Icon (optional)</span></label>
          <input v-model="form.icon" type="text" class="input input-bordered" maxlength="50" placeholder="e.g. 🍕" />
        </div>
      </div>
      <p v-if="errorMessage" class="text-error text-sm">{{ errorMessage }}</p>
      <button type="submit" class="btn btn-primary w-fit">Save category</button>
    </form>

    <div v-if="categoryStore.loading" class="text-base-content/60">Loading categories...</div>

    <div v-else-if="categoryStore.categories.length === 0" class="card bg-base-100 shadow-sm p-10 text-center text-base-content/60">
      No categories found. Create your first one.
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="cat in categoryStore.categories" :key="cat.id" class="card bg-base-100 shadow-sm">
        <div class="card-body flex flex-row items-center gap-4">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl" :style="{ backgroundColor: (cat.color || '#94a3b8') + '20' }">
            {{ cat.icon || '🏷️' }}
          </div>
          <div>
            <h3 class="font-semibold">{{ cat.name }}</h3>
            <p class="text-xs text-base-content/50">{{ cat.color || 'No color' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
