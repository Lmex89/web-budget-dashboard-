<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const isSubmitting = ref(false)

async function handleSubmit() {
  isSubmitting.value = true
  error.value = ''
  try {
    await authStore.login(email.value, password.value)
    router.push('/')
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || 'Invalid credentials'
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
          <div class="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center text-primary-content font-bold text-2xl mx-auto mb-4">
            FB
          </div>
          <h1 class="text-2xl font-bold">Welcome back</h1>
          <p class="text-base-content/60 text-sm mt-1">Sign in to your Family Budget</p>
        </div>

        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Email</span>
            </label>
            <input
              v-model="email"
              type="email"
              placeholder="your@email.com"
              class="input input-bordered w-full"
              required
              autocomplete="email"
            />
          </div>

          <div class="form-control">
            <label class="label">
              <span class="label-text">Password</span>
            </label>
            <input
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="input input-bordered w-full"
              required
              autocomplete="current-password"
            />
          </div>

          <div v-if="error" class="alert alert-error text-sm py-2">
            {{ error }}
          </div>

          <button
            type="submit"
            class="btn btn-primary w-full"
            :class="{ 'loading': isSubmitting }"
            :disabled="isSubmitting"
          >
            Sign In
          </button>
        </form>

        <p class="text-center text-sm text-base-content/60 mt-6">
          Don't have an account?
          <router-link to="/register" class="link link-primary">Create one</router-link>
        </p>
      </div>
    </div>
  </div>
</template>
