<template>
  <div
    class="flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg text-sm font-medium
           transition-all duration-300 max-w-sm"
    :class="typeClass"
    role="alert"
  >
    <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="icon"/>
    </svg>
    <span class="flex-1">{{ message }}</span>
    <button @click="$emit('dismiss')" class="flex-shrink-0 opacity-60 hover:opacity-100">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: { type: String, required: true },
  type: { type: String, default: 'info' },
})

defineEmits(['dismiss'])

const typeClass = computed(() => ({
  success: 'bg-green-600 text-white',
  error: 'bg-red-600 text-white',
  info: 'bg-gray-800 text-white',
}[props.type] || 'bg-gray-800 text-white'))

const icon = computed(() => ({
  success: 'M5 13l4 4L19 7',
  error: 'M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  info: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
}[props.type] || 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'))
</script>
