<template>
  <div class="min-h-screen bg-light-gray flex items-center justify-center px-4 py-16">
    <div class="card p-8 w-full max-w-sm">
      <!-- Logo/brand -->
      <div class="text-center mb-6">
        <img v-if="shop.logo" :src="shop.logo" alt="Logo" class="h-10 mx-auto mb-3" />
        <h1 class="text-xl font-bold text-gray-900">{{ shop.shopName }}</h1>
        <p class="text-sm text-gray-500 mt-1">Sign in to your account</p>
      </div>

      <form class="space-y-4" @submit.prevent="signIn">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
          <input
            v-model="email"
            type="email"
            required
            autocomplete="username"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
          />
        </div>

        <div v-if="error" class="p-3 rounded bg-red-50 border border-red-200 text-red-700 text-sm">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3 rounded-lg text-white font-semibold text-sm disabled:opacity-50 transition-all"
          :style="{ backgroundColor: 'var(--shop-primary)' }"
        >
          {{ loading ? 'Signing in…' : 'Sign In' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <router-link to="/products" class="text-sm text-gray-500 hover:text-gray-700">
          Continue Shopping without signing in →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useShopStore } from '../stores/shop.js'
import { useAuthStore } from '../stores/auth.js'

const router = useRouter()
const route = useRoute()
const shop = useShopStore()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function signIn() {
  loading.value = true
  error.value = ''
  try {
    const body = new URLSearchParams({ usr: email.value, pwd: password.value })
    const res = await fetch('/api/method/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: body.toString(),
    })
    const json = await res.json().catch(() => ({}))
    if (json.message === 'Logged In') {
      const returnUrl = route.query.returnUrl || '/account'
      window.location.href = '/shop#' + returnUrl
    } else {
      error.value = 'Invalid email or password.'
    }
  } catch (_) {
    error.value = 'Network error. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
