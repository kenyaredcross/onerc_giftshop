<template>
  <div class="max-w-lg mx-auto px-4 py-16 text-center">
    <!-- Green check -->
    <div class="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-6">
      <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/>
      </svg>
    </div>

    <h1 class="text-2xl font-bold mb-1" :style="{ color: 'var(--shop-primary)' }">Order Confirmed!</h1>
    <p class="text-gray-500 text-sm mb-6">
      You will receive an SMS confirmation shortly.
    </p>

    <div v-if="loading" class="flex justify-center mb-6">
      <LoadingSpinner />
    </div>

    <template v-else-if="order">
      <div class="card p-5 text-left mb-6">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Order Number</p>
        <p class="text-lg font-bold text-gray-900 mb-4">{{ order.order_number }}</p>

        <div v-if="order.items && order.items.length" class="space-y-2 mb-4">
          <div
            v-for="item in order.items"
            :key="item.item_code"
            class="flex justify-between text-sm text-gray-700"
          >
            <span class="flex-1 truncate mr-2">{{ item.item_name }} × {{ item.quantity }}</span>
            <span class="flex-shrink-0">{{ fmtCurrency(item.line_total) }}</span>
          </div>
        </div>

        <div class="border-t border-gray-100 pt-3 flex justify-between font-bold text-gray-900">
          <span>Total</span>
          <span>{{ fmtCurrency(order.total) }}</span>
        </div>
      </div>
    </template>

    <div class="flex flex-col sm:flex-row gap-3 justify-center">
      <router-link to="/products">
        <button
          class="px-6 py-2.5 rounded-lg text-white font-semibold text-sm"
          :style="{ backgroundColor: 'var(--shop-primary)' }"
        >Continue Shopping</button>
      </router-link>
      <router-link v-if="orderNumber" :to="`/account/orders/${orderNumber}`">
        <button class="px-6 py-2.5 rounded-lg font-semibold text-sm border border-gray-300 hover:bg-gray-50">
          View Order
        </button>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useApi } from '../composables/useApi.js'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const route = useRoute()
const cart = useCartStore()
const { getOrder } = useApi()

const orderNumber = ref(route.query.order || '')
const loading = ref(false)
const order = ref(null)

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 })
    .format(Number(v) || 0)
}

onMounted(async () => {
  cart.clearCart()
  if (!orderNumber.value) return
  loading.value = true
  try {
    const res = await getOrder(orderNumber.value)
    if (res?.status === 'success') order.value = res.data
  } catch (_) { /* order details unavailable, page still shows */ }
  finally { loading.value = false }
})
</script>
