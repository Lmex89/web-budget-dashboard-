<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import FormField from '@/components/ui/FormField.vue'
import PaperCard from '@/components/ui/PaperCard.vue'
import type { RegisterPayload } from '@/types'

const router = useRouter()
const authStore = useAuthStore()

const form = ref<RegisterPayload>({
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
  } catch (err: unknown) {
    if (err && typeof err === 'object' && 'response' in err) {
      const response = (err as { response?: { data?: { error?: { message?: string } } } }).response
      error.value = response?.data?.error?.message || 'Registration failed'
    } else {
      error.value = 'Registration failed'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center px-5 py-12 bg-paper">
    <div class="w-full max-w-md animate-fade-up">
      <div class="text-center mb-10">
        <div class="w-14 h-14 mx-auto mb-6 rounded-2xl bg-accent text-white flex items-center justify-center font-display text-xl font-semibold shadow-paper">
          FB
        </div>
        <h1 class="font-display text-[2rem] font-bold tracking-tight text-ink">Create account</h1>
        <p class="text-sm text-muted mt-1.5">Join or create a family budget</p>
      </div>

      <PaperCard class="p-6 md:p-8">
        <form @submit.prevent="handleSubmit" class="space-y-5">
          <FormField label="Full name" for-id="reg-name">
            <input id="reg-name" v-model="form.full_name" type="text" class="eb-input" placeholder="Jane Doe" required />
          </FormField>

          <FormField label="Email" for-id="reg-email">
            <input id="reg-email" v-model="form.email" type="email" class="eb-input" placeholder="your@email.com" required />
          </FormField>

          <FormField label="Password" for-id="reg-password">
            <input id="reg-password" v-model="form.password" type="password" class="eb-input" placeholder="At least 8 characters" required minlength="8" />
          </FormField>

          <FormField label="Family name" for-id="reg-family">
            <input id="reg-family" v-model="form.family_name" type="text" class="eb-input" placeholder="e.g. Smith Family" required />
          </FormField>

          <p v-if="error" class="text-sm font-medium text-danger">{{ error }}</p>

          <button type="submit" class="eb-btn eb-btn-primary w-full" :disabled="isSubmitting">
            {{ isSubmitting ? 'Creating…' : 'Create account' }}
          </button>
        </form>
      </PaperCard>

      <p class="text-center text-sm text-muted mt-8">
        Already have one?
        <router-link to="/login" class="font-semibold text-accent hover:underline">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>
