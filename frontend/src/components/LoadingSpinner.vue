<template>
  <svg
    :class="sizeClass"
    class="animate-spin"
    :style="{ color: 'var(--shop-primary)' }"
    fill="none"
    viewBox="0 0 24 24"
    aria-label="Loading"
  >
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: { type: String, default: 'md' },
})

const sizeClass = computed(() => ({
  sm: 'w-4 h-4',
  md: 'w-6 h-6',
  lg: 'w-10 h-10',
}[props.size] || 'w-6 h-6'))
</script>
