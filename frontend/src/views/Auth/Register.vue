<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  full_name: '',
  family_name: '',
})
const error = ref('')
const isSubmitting = ref(false)

async function handleSubmit() {
  isSubmitting.value = true
  error.value = ''
  try {
    await api.post('/api/v1/auth/register', form.value)
    await authStore.login(form.value.email, form.value.password)
    router.push('/')
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Registration failed'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-base-200 px-4">
    <div class="card w-full max-w-md bg-base-100 shadow-xl">
      <div class="card-body p-8">
        <div class="text-center mb-8">
          <div class="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center text-primary-content font-bold text-2xl mx-auto mb-4">FB</div>
          <h1 class="text-2xl font-bold">Create account</h1>
          <p class="text-base-content/60 text-sm mt-1">Join or create a family budget</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="form-control">
            <label class="label"><span class="label-text">Full name</span></label>
            <input v-model="form.full_name" type="text" class="input input-bordered w-full" required />
          </div>
          <div class="form-control">
            <label class="label"><span class="label-text">Email</span></label>
            <input v-model="form.email" type="email" class="input input-bordered w-full" required />
          </div>
          <div class="form-control">
            <label class="label"><span class="label-text">Password</span></label>
            <input v-model="form.password" type="password" class="input input-bordered w-full" required minlength="8" />
          </div>
          <div class="form-control">
            <label class="label"><span class="label-text">Family name</span></label>
            <input v-model="form.family_name" type="text" placeholder="e.g. Smith Family" class="input input-bordered w-full" required />
          </div>

          <div v-if="error" class="alert alert-error text-sm py-2">{{ error }}</div>

          <button type="submit" class="btn btn-primary w-full" :class="{ loading: isSubmitting }" :disabled="isSubmitting">
            Create account
          </button>
        </form>

        <p class="text-center text-sm text-base-content/60 mt-6">
          Already have one?
          <router-link to="/login" class="link link-primary">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
