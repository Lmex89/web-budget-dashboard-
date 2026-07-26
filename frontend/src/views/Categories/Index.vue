<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import FormField from '@/components/ui/FormField.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { useForm } from '@/composables/useForm'
import type { CreateCategoryPayload, UpdateCategoryPayload } from '@/types'

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

interface EditingState {
  categoryId: string
  name: string
  color: string
  icon: string
  saving: boolean
  error: string | null
}

const editing = ref<EditingState | null>(null)
const editInputRef = ref<HTMLInputElement | null>(null)
const deleting = ref<Record<string, boolean>>({})

function startEdit(categoryId: string, currentName: string, currentColor: string | null, currentIcon: string | null) {
  editing.value = {
    categoryId,
    name: currentName,
    color: currentColor || '#0071e3',
    icon: currentIcon || '',
    saving: false,
    error: null,
  }
  nextTick(() => {
    editInputRef.value?.focus()
    editInputRef.value?.select()
  })
}

function cancelEdit() {
  editing.value = null
}

async function saveEdit(categoryId: string) {
  const state = editing.value
  if (!state) return
  const trimmed = state.name.trim()
  if (!trimmed) {
    state.error = 'Name is required'
    return
  }
  state.saving = true
  state.error = null
  try {
    const payload: UpdateCategoryPayload = {
      name: trimmed,
      color: state.color || null,
      icon: (state.icon || '').trim() || null,
    }
    await categoryStore.updateCategory(categoryId, payload)
    editing.value = null
  } catch (e: unknown) {
    state.saving = false
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    state.error = err?.response?.data?.error?.message || 'Failed to save'
  }
}

function onEditKeydown(event: KeyboardEvent, categoryId: string) {
  if (event.key === 'Enter') {
    event.preventDefault()
    saveEdit(categoryId)
  } else if (event.key === 'Escape') {
    cancelEdit()
  }
}

async function handleDelete(categoryId: string, name: string) {
  if (!window.confirm(`Delete category "${name}"?`)) return
  deleting.value[categoryId] = true
  try {
    await categoryStore.deleteCategory(categoryId)
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    alert(err?.response?.data?.error?.message || 'Failed to delete category')
  } finally {
    deleting.value[categoryId] = false
  }
}

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
          class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl shrink-0 overflow-hidden"
          :style="{ backgroundColor: (cat.color || '#a8a29e') + '20' }"
        >
          <span class="truncate px-1">{{ cat.icon || '🏷️' }}</span>
        </div>
        <div class="min-w-0 flex-1">
          <div v-if="editing?.categoryId === cat.id" class="space-y-2 w-full">
            <div class="flex items-center gap-2">
              <input
                ref="editInputRef"
                v-model="editing.name"
                type="text"
                class="eb-input text-sm flex-1 min-w-0"
                maxlength="100"
                :disabled="editing.saving"
                placeholder="Name"
                @keydown="onEditKeydown($event, cat.id)"
              />
              <input
                v-model="editing.color"
                type="color"
                class="w-9 h-9 p-0.5 bg-paper-2 border border-rule rounded-lg cursor-pointer shrink-0"
                :disabled="editing.saving"
              />
            </div>
            <div class="flex items-center gap-2">
              <input
                v-model="editing.icon"
                type="text"
                class="eb-input text-sm flex-1"
                maxlength="50"
                placeholder="Icon e.g. 🍕"
                :disabled="editing.saving"
              />
              <button
                class="eb-btn eb-btn-primary text-xs px-3 py-1 shrink-0"
                :disabled="editing.saving"
                @click="saveEdit(cat.id)"
              >Save</button>
              <button
                class="eb-btn eb-btn-ghost text-xs px-3 py-1 shrink-0"
                :disabled="editing.saving"
                @click="cancelEdit"
              >Cancel</button>
            </div>
            <p v-if="editing.error" class="text-xs text-danger">{{ editing.error }}</p>
          </div>
          <div v-else class="group cursor-pointer" @click="startEdit(cat.id, cat.name, cat.color, cat.icon)">
            <h3 class="font-semibold truncate group-hover:text-accent transition-colors">{{ cat.name }}</h3>
            <p class="text-xs text-muted mt-0.5 uppercase tracking-wide">{{ cat.color || 'No color' }}</p>
          </div>
        </div>
        <button
          class="text-xs text-danger hover:underline shrink-0 px-1"
          :disabled="deleting[cat.id]"
          @click="handleDelete(cat.id, cat.name)"
        >
          Delete
        </button>
      </PaperCard>
    </div>
  </div>
</template>
