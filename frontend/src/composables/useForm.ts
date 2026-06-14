import { shallowRef, ref } from 'vue'

interface UseFormOptions<T> {
  initialValues: T
  onSubmit: (values: T) => Promise<void>
}

interface UseFormReturn<T> {
  form: ReturnType<typeof shallowRef<T>>
  showForm: ReturnType<typeof ref<boolean>>
  errorMessage: ReturnType<typeof ref<string>>
  isSubmitting: ReturnType<typeof ref<boolean>>
  handleSubmit: () => Promise<void>
  resetForm: () => void
  toggleForm: () => void
}

export function useForm<T extends object>(options: UseFormOptions<T>): UseFormReturn<T> {
  const { initialValues, onSubmit } = options

  const form = shallowRef<T>({ ...initialValues })
  const showForm = ref(false)
  const errorMessage = ref('')
  const isSubmitting = ref(false)

  function resetForm() {
    form.value = { ...initialValues }
    errorMessage.value = ''
  }

  function toggleForm() {
    showForm.value = !showForm.value
  }

  async function handleSubmit() {
    errorMessage.value = ''
    isSubmitting.value = true
    try {
      await onSubmit(form.value)
      showForm.value = false
      resetForm()
    } catch (error: unknown) {
      errorMessage.value = extractErrorMessage(error)
    } finally {
      isSubmitting.value = false
    }
  }

  return {
    form,
    showForm,
    errorMessage,
    isSubmitting,
    handleSubmit,
    resetForm,
    toggleForm,
  }
}

function extractErrorMessage(error: unknown): string {
  if (error && typeof error === 'object' && 'response' in error) {
    const response = (error as { response?: { data?: { error?: { message?: string } } } }).response
    if (response?.data?.error?.message) {
      return response.data.error.message
    }
  }
  if (error instanceof Error) {
    return error.message
  }
  return 'An error occurred'
}
