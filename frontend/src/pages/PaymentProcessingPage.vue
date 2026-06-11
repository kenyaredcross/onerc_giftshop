<template>
  <div class="flex flex-col items-center justify-center min-h-[60vh] px-4 py-16">
    <template v-if="!timedOut">
      <LoadingSpinner size="lg" />
      <h2 class="mt-6 text-lg font-semibold text-gray-800">Waiting for payment confirmation</h2>
      <p class="mt-2 text-sm text-gray-500">Order: <span class="font-mono font-medium">{{ orderNumber }}</span></p>
      <p class="mt-4 text-xs text-gray-400">Keep this page open. Do not refresh.</p>
    </template>
    <template v-else>
      <svg class="w-12 h-12 text-yellow-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <h2 class="text-lg font-semibold text-gray-800 mb-2">This is taking longer than expected</h2>
      <p class="text-sm text-gray-500 mb-6 text-center max-w-sm">
        Your payment may still be processing. Check your order status or try again.
      </p>
      <div class="flex flex-col items-center gap-3">
        <router-link to="/account" class="text-sm underline text-gray-600">Check my order status</router-link>
        <router-link to="/checkout" class="text-sm underline text-gray-600">Try again</router-link>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../composables/useApi.js'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const { getOrder } = useApi()

const orderNumber = ref(route.query.order || '')
const timedOut = ref(false)
let attempts = 0
let intervalId = null

async function poll() {
  attempts++
  if (attempts > 20) {
    clearInterval(intervalId)
    timedOut.value = true
    return
  }

  try {
    const res = await getOrder(orderNumber.value)
    if (res?.status === 'success') {
      const status = res.data?.status
      if (status && status !== 'Pending Payment') {
        clearInterval(intervalId)
        if (status === 'Confirmed' || status === 'Processing') {
          router.push(`/checkout/success?order=${orderNumber.value}`)
        } else {
          router.push('/checkout?error=payment_failed')
        }
      }
    }
  } catch (_) { /* keep polling */ }
}

onMounted(() => {
  if (!orderNumber.value) { router.replace('/cart'); return }
  intervalId = setInterval(poll, 3000)
  poll()
})

onUnmounted(() => clearInterval(intervalId))
</script>
