<template>
  <div class="relative inline-block">
    <select
      :value="modelValue"
      :disabled="loading || disabled"
      class="appearance-none pl-3 pr-8 py-1.5 text-xs font-medium border rounded-full
             focus:outline-none focus:ring-2 focus:ring-primary cursor-pointer
             disabled:opacity-50 disabled:cursor-not-allowed"
      :class="statusClass"
      @change="handleChange"
    >
      <option v-for="opt in options" :key="opt.value" :value="opt.value">
        {{ opt.label }}
      </option>
    </select>
    <span v-if="loading" class="absolute right-2 top-1/2 -translate-y-1/2">
      <svg class="w-3 h-3 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: String, required: true },
  options: { type: Array, required: true },
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'change'])

function handleChange(e) {
  emit('update:modelValue', e.target.value)
  emit('change', e.target.value)
}

const STATUS_CLASSES = {
  'Pending Payment': 'bg-yellow-50 border-yellow-300 text-yellow-800',
  Confirmed: 'bg-blue-50 border-blue-300 text-blue-800',
  Processing: 'bg-indigo-50 border-indigo-300 text-indigo-800',
  'Ready for Collection': 'bg-purple-50 border-purple-300 text-purple-800',
  Delivered: 'bg-green-50 border-green-300 text-green-800',
  Cancelled: 'bg-red-50 border-red-300 text-red-800',
  Active: 'bg-green-50 border-green-300 text-green-800',
  Inactive: 'bg-gray-50 border-gray-300 text-gray-700',
}

const statusClass = computed(
  () => STATUS_CLASSES[props.modelValue] || 'bg-gray-50 border-gray-300 text-gray-700'
)
</script>
