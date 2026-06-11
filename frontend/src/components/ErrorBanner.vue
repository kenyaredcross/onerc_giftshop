<template>
  <div v-if="visible" class="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
    <svg class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
    </svg>
    <p class="flex-1">{{ message }}</p>
    <button v-if="dismissable" @click="visible = false" class="flex-shrink-0 text-red-400 hover:text-red-600">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  message: { type: String, required: true },
  dismissable: { type: Boolean, default: true },
})

const emit = defineEmits(['dismiss'])
const visible = ref(true)

watch(() => props.message, () => { visible.value = true })

watch(visible, (v) => { if (!v) emit('dismiss') })
</script>
