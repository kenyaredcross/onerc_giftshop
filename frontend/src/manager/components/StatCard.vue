<template>
  <div class="card p-5">
    <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">{{ label }}</p>
    <p class="mt-2 text-2xl font-bold text-gray-900">{{ formattedValue }}</p>
    <p v-if="sub" class="mt-1 text-xs text-gray-400">{{ sub }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], default: 0 },
  currency: { type: Boolean, default: false },
  sub: { type: String, default: '' },
})

const formattedValue = computed(() => {
  if (props.currency) {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
    }).format(Number(props.value) || 0)
  }
  return props.value
})
</script>
