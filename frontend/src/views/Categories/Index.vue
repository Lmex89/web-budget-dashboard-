<script setup lang="ts">
import { onMounted } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import FormField from '@/components/ui/FormField.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { useForm } from '@/composables/useForm'
import type { CreateCategoryPayload } from '@/types'

const categoryStore = useCategoryStore()

interface CategoryForm {
  name: string
  color: string
  icon: string
}

const initialForm: CategoryForm = {
  name: '',
  color: '#0071e3',
  icon: '',
}

const { form, showForm, errorMessage, toggleForm, handleSubmit } = useForm<CategoryForm>({
  initialValues: initialForm,
  onSubmit: async (values) => {
    const payload: CreateCategoryPayload = {
      name: values.name.trim(),
      color: values.color || null,
      icon: values.icon.trim() || null,
    }
    await categoryStore.createCategory(payload)
  },
})

onMounted(async () => {
  await categoryStore.fetchCategories()
})
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Categories" subtitle="Organize spending the way your family thinks about it.">
      <template #action>
        <button class="eb-btn" :class="showForm ? 'eb-btn-ghost' : 'eb-btn-primary'" @click="toggleForm">
          {{ showForm ? 'Cancel' : 'Add category' }}
        </button>
      </template>
    </PageHeader>

    <form
      v-if="showForm"
      @submit.prevent="handleSubmit"
      class="paper-card p-5 md:p-6 space-y-5 animate-fade-up"
    >
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <FormField label="Name" for-id="cat-name" class="md:col-span-2">
          <input
            id="cat-name"
            v-model="form.name"
            type="text"
            class="eb-input"
            maxlength="100"
            placeholder="e.g. Groceries"
            required
          />
        </FormField>

        <FormField label="Color" for-id="cat-color">
          <div class="flex items-center gap-3">
            <input
              id="cat-color"
              v-model="form.color"
              type="color"
              class="w-14 h-11 p-1 bg-paper-2 border border-rule rounded-lg cursor-pointer"
            />
            <span class="text-xs text-muted uppercase tracking-wide">{{ form.color }}</span>
          </div>
        </FormField>

        <FormField label="Icon (optional)" for-id="cat-icon" class="md:col-span-3">
          <input
            id="cat-icon"
            v-model="form.icon"
            type="text"
            class="eb-input"
            maxlength="50"
            placeholder="e.g. 🍕"
          />
        </FormField>
      </div>

      <p v-if="errorMessage" class="text-sm font-medium text-danger">{{ errorMessage }}</p>

      <div class="flex items-center gap-3">
        <button type="submit" class="eb-btn eb-btn-primary">Save category</button>
        <button type="button" class="eb-btn eb-btn-ghost" @click="showForm = false">Cancel</button>
      </div>
    </form>

    <div v-if="categoryStore.loading" class="text-sm text-muted animate-pulse">Loading categories…</div>

    <EmptyState
      v-else-if="categoryStore.categories.length === 0"
      title="No categories"
      description="Create a category to group your spending."
    >
      <template #icon>🏷️</template>
      <template #action>
        <button class="eb-btn eb-btn-primary" @click="showForm = true">Add category</button>
      </template>
    </EmptyState>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <PaperCard
        v-for="cat in categoryStore.categories"
        :key="cat.id"
        class="p-4 flex items-center gap-4 animate-fade-up"
      >
        <div
          class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0"
          :style="{ backgroundColor: (cat.color || '#a8a29e') + '20' }"
        >
          {{ cat.icon || '🏷️' }}
        </div>
        <div class="min-w-0">
          <h3 class="font-semibold truncate">{{ cat.name }}</h3>
          <p class="text-xs text-muted mt-0.5 uppercase tracking-wide">{{ cat.color || 'No color' }}</p>
        </div>
      </PaperCard>
    </div>
  </div>
</template>
