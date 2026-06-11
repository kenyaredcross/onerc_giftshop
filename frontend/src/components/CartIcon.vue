<template>
  <button class="relative p-2 text-gray-600 hover:text-gray-900" @click="$router.push('/cart')" aria-label="Cart">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
        d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
    </svg>
    <span
      v-if="cart.itemCount > 0"
      class="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 rounded-full
             text-white text-xs font-bold flex items-center justify-center"
      :style="{ backgroundColor: 'var(--shop-primary)' }"
    >
      {{ cart.itemCount > 99 ? '99+' : cart.itemCount }}
    </span>
  </button>
</template>

<script setup>
import { useCartStore } from '../stores/cart.js'
const cart = useCartStore()
</script>
