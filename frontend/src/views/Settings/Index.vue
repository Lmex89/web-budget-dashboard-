<script setup lang="ts">
import { shallowRef, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import PageHeader from '@/components/ui/PageHeader.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import FormField from '@/components/ui/FormField.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import { useForm } from '@/composables/useForm'
import type { User, CreateMemberPayload } from '@/types'

const authStore = useAuthStore()
const users = shallowRef<User[]>([])

interface MemberForm {
  email: string
  password: string
  full_name: string
}

const initialForm: MemberForm = {
  email: '',
  password: '',
  full_name: '',
}

const { form, showForm, errorMessage, toggleForm, handleSubmit } = useForm<MemberForm>({
  initialValues: initialForm,
  onSubmit: async (values) => {
    const payload: CreateMemberPayload = values
    await api.post('/api/v1/auth/users', payload)
    await fetchUsers()
  },
})

async function fetchUsers() {
  const { data } = await api.get('/api/v1/auth/users')
  if (data.success) users.value = data.data
}

onMounted(fetchUsers)
</script>

<template>
  <div class="space-y-6">
    <PageHeader title="Family" subtitle="Manage who shares this budget.">
      <template #action>
        <button
          v-if="authStore.user?.is_admin"
          class="eb-btn"
          :class="showForm ? 'eb-btn-ghost' : 'eb-btn-primary'"
          @click="toggleForm"
        >
          {{ showForm ? 'Cancel' : 'Add member' }}
        </button>
      </template>
    </PageHeader>

    <form
      v-if="showForm"
      @submit.prevent="handleSubmit"
      class="paper-card p-5 md:p-6 space-y-5 animate-fade-up"
    >
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        <FormField label="Full name" for-id="user-name">
          <input id="user-name" v-model="form.full_name" type="text" class="eb-input" placeholder="Jane Doe" required />
        </FormField>
        <FormField label="Email" for-id="user-email">
          <input id="user-email" v-model="form.email" type="email" class="eb-input" placeholder="jane@example.com" required />
        </FormField>
        <FormField label="Password" for-id="user-password">
          <input id="user-password" v-model="form.password" type="password" class="eb-input" placeholder="••••••••" required minlength="8" />
        </FormField>
      </div>
      <p v-if="errorMessage" class="text-sm font-medium text-danger">{{ errorMessage }}</p>
      <div class="flex items-center gap-3">
        <button type="submit" class="eb-btn eb-btn-primary">Add member</button>
        <button type="button" class="eb-btn eb-btn-ghost" @click="showForm = false">Cancel</button>
      </div>
    </form>

    <div v-if="users.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <PaperCard
        v-for="u in users"
        :key="u.id"
        class="p-5 flex items-center gap-4 animate-fade-up"
      >
        <div class="w-12 h-12 rounded-full bg-ink text-paper flex items-center justify-center text-base font-semibold shrink-0">
          {{ u.full_name?.charAt(0) || 'U' }}
        </div>
        <div class="min-w-0 flex-1">
          <p class="font-semibold truncate">{{ u.full_name }}</p>
          <p class="text-xs text-muted truncate">{{ u.email }}</p>
        </div>
        <div class="flex flex-col items-end gap-1.5 shrink-0">
          <span class="chip" :class="u.is_admin ? 'chip-accent' : 'chip-muted'">
            {{ u.is_admin ? 'Admin' : 'Member' }}
          </span>
          <span class="chip" :class="u.is_active ? 'chip-sage' : 'chip-danger'">
            {{ u.is_active ? 'Active' : 'Inactive' }}
          </span>
        </div>
      </PaperCard>
    </div>

    <EmptyState v-else title="No family members" description="Invite the people who share your budget.">
      <template #icon>👋</template>
    </EmptyState>
  </div>
</template>
