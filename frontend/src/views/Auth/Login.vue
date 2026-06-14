<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import FormField from '@/components/ui/FormField.vue'
import PaperCard from '@/components/ui/PaperCard.vue'

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
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const response = (err as { response?: { data?: { error?: { message?: string } } } }).response
      error.value = response?.data?.error?.message || 'Invalid credentials'
    } else {
      error.value = 'Invalid credentials'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-5 py-12 bg-paper relative overflow-hidden">
    <div class="absolute -top-24 -right-24 w-72 h-72 rounded-full bg-accent/5 blur-3xl" />
    <div class="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-sage/5 blur-3xl" />

    <div class="w-full max-w-md z-10 animate-fade-up">
      <div class="text-center mb-8">
        <div class="w-16 h-16 rounded-2xl bg-ink text-paper flex items-center justify-center font-display text-2xl mx-auto mb-5 shadow-paper">
          FB
        </div>
        <h1 class="font-display text-4xl tracking-tight">Welcome back</h1>
        <p class="text-sm text-muted mt-2">Sign in to your Family Budget</p>
      </div>

      <PaperCard class="p-6 md:p-8">
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <FormField label="Email" for-id="login-email">
            <input
              id="login-email"
              v-model="email"
              type="email"
              placeholder="your@email.com"
              class="eb-input"
              required
              autocomplete="email"
            />
          </FormField>

          <FormField label="Password" for-id="login-password">
            <input
              id="login-password"
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="eb-input"
              required
              autocomplete="current-password"
            />
          </FormField>

          <p v-if="error" class="text-sm font-medium text-danger">{{ error }}</p>

          <button
            type="submit"
            class="eb-btn eb-btn-primary w-full"
            :disabled="isSubmitting"
          >
            {{ isSubmitting ? 'Signing in…' : 'Sign In' }}
          </button>
        </form>
      </PaperCard>

      <p class="text-center text-sm text-muted mt-6">
        Don't have an account?
        <router-link to="/register" class="font-semibold text-ink underline decoration-accent underline-offset-4 hover:text-accent">
          Create one
        </router-link>
      </p>
    </div>
  </div>
</template>
