<template>
  <button
    class="flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium border transition-all duration-150 focus:outline-none"
    :class="active
      ? 'text-white border-transparent'
      : 'bg-white text-gray-700 border-gray-300 hover:border-gray-400'"
    :style="active ? { backgroundColor: 'var(--shop-primary)', borderColor: 'var(--shop-primary)' } : {}"
    @click="$emit('select', slug)"
  >
    {{ name }}
  </button>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  slug: { type: String, required: true },
  active: { type: Boolean, default: false },
})
defineEmits(['select'])
</script>
