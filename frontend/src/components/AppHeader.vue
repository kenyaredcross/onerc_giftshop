<template>
  <header class="bg-white border-b border-gray-100 shadow-sm sticky top-0 z-40">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-4">
      <!-- Logo / Name -->
      <router-link to="/" class="flex items-center gap-2 flex-shrink-0">
        <img v-if="shop.logo" :src="shop.logo" alt="Shop logo" class="h-8 w-auto" />
        <span v-else class="font-bold text-lg" :style="{ color: 'var(--shop-secondary)' }">
          {{ shop.shopName }}
        </span>
      </router-link>

      <!-- Desktop nav -->
      <nav class="hidden md:flex items-center gap-6 text-sm font-medium text-gray-600">
        <router-link to="/" class="hover:text-gray-900 transition-colors">Home</router-link>
        <router-link to="/products" class="hover:text-gray-900 transition-colors">Shop</router-link>
      </nav>

      <!-- Right actions -->
      <div class="flex items-center gap-3">
        <CartIcon />
        <template v-if="auth.isGuest">
          <router-link to="/login" class="text-sm font-medium text-gray-600 hover:text-gray-900">Sign In</router-link>
        </template>
        <template v-else>
          <router-link to="/account" class="text-sm font-medium text-gray-600 hover:text-gray-900">
            {{ auth.fullName }}
          </router-link>
        </template>

        <!-- Mobile hamburger -->
        <button
          class="md:hidden p-2 text-gray-500 hover:text-gray-900"
          @click="menuOpen = !menuOpen"
          aria-label="Menu"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              :d="menuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Mobile dropdown -->
    <div v-if="menuOpen" class="md:hidden border-t border-gray-100 bg-white px-4 py-3 space-y-2">
      <router-link to="/" class="block text-sm text-gray-700 py-1" @click="menuOpen = false">Home</router-link>
      <router-link to="/products" class="block text-sm text-gray-700 py-1" @click="menuOpen = false">Shop</router-link>
      <template v-if="!auth.isGuest">
        <router-link to="/account" class="block text-sm text-gray-700 py-1" @click="menuOpen = false">My Account</router-link>
      </template>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useShopStore } from '../stores/shop.js'
import { useAuthStore } from '../stores/auth.js'
import CartIcon from './CartIcon.vue'

const shop = useShopStore()
const auth = useAuthStore()
const menuOpen = ref(false)
</script>
