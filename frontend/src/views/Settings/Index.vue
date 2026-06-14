<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const authStore = useAuthStore()
const users = ref<any[]>([])
const showForm = ref(false)
const form = ref({ email: '', password: '', full_name: '' })
const error = ref('')

async function fetchUsers() {
  const { data } = await api.get('/api/v1/auth/users')
  if (data.success) users.value = data.data
}

async function addUser() {
  error.value = ''
  try {
    await api.post('/api/v1/auth/users', form.value)
    showForm.value = false
    form.value = { email: '', password: '', full_name: '' }
    await fetchUsers()
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Failed to add user'
  }
}

onMounted(fetchUsers)
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Family members</h1>
        <p class="text-base-content/60 text-sm">Manage who has access to this family budget</p>
      </div>
      <button v-if="authStore.user?.is_admin" class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? 'Cancel' : '+ Add member' }}
      </button>
    </div>

    <form v-if="showForm" @submit.prevent="addUser" class="card bg-base-100 shadow-sm p-6 space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <input v-model="form.full_name" placeholder="Full name" class="input input-bordered" required />
        <input v-model="form.email" type="email" placeholder="Email" class="input input-bordered" required />
        <input v-model="form.password" type="password" placeholder="Password" class="input input-bordered" required minlength="8" />
      </div>
      <div v-if="error" class="alert alert-error text-sm py-2">{{ error }}</div>
      <button type="submit" class="btn btn-primary">Add</button>
    </form>

    <div class="overflow-x-auto">
      <table class="table table-zebra">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Role</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td class="font-medium">{{ u.full_name }}</td>
            <td>{{ u.email }}</td>
            <td><span class="badge" :class="u.is_admin ? 'badge-primary' : 'badge-ghost'">{{ u.is_admin ? 'Admin' : 'Member' }}</span></td>
            <td><span class="badge" :class="u.is_active ? 'badge-success' : 'badge-error'">{{ u.is_active ? 'Active' : 'Inactive' }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
