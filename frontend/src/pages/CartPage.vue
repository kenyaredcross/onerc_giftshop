<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Your Cart</h1>

    <div v-if="cart.loading" class="flex justify-center py-16">
      <LoadingSpinner size="lg" />
    </div>

    <div v-else-if="cart.isEmpty" class="text-center py-20">
      <svg class="w-16 h-16 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
      </svg>
      <p class="text-gray-500 mb-4">Your cart is empty</p>
      <router-link to="/products">
        <button
          class="px-6 py-2.5 rounded-lg text-white font-semibold text-sm"
          :style="{ backgroundColor: 'var(--shop-primary)' }"
        >Continue Shopping</button>
      </router-link>
    </div>

    <div v-else class="grid lg:grid-cols-3 gap-6">
      <!-- Cart items -->
      <div class="lg:col-span-2 space-y-3">
        <ErrorBanner v-if="cart.error" :message="cart.error" />
        <div
          v-for="item in cart.items"
          :key="item.slug || item.listing"
          class="card p-4 flex items-center gap-4"
        >
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900 text-sm truncate">{{ item.item_name }}</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ fmtCurrency(item.unit_price) }} each</p>
          </div>
          <div class="flex items-center gap-2">
            <input
              :value="item.quantity"
              type="number"
              min="1"
              max="99"
              class="w-16 border border-gray-300 rounded-lg px-2 py-1 text-sm text-center"
              @change="onQtyChange(item.slug, $event.target.value)"
            />
            <button
              class="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
              @click="cart.updateItem(item.slug, 0)"
              title="Remove"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
              </svg>
            </button>
          </div>
          <div class="w-20 text-right font-semibold text-sm text-gray-900">
            {{ fmtCurrency(item.line_total) }}
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div class="lg:col-span-1">
        <div class="card p-5 space-y-3 sticky top-20">
          <h2 class="font-semibold text-gray-800">Order Summary</h2>
          <div class="flex justify-between text-sm text-gray-600">
            <span>Subtotal</span><span>{{ fmtCurrency(cart.subtotal) }}</span>
          </div>
          <div v-if="cart.tax_amount > 0" class="flex justify-between text-sm text-gray-600">
            <span>Tax</span><span>{{ fmtCurrency(cart.tax_amount) }}</span>
          </div>
          <div class="border-t border-gray-100 pt-3 flex justify-between font-bold text-gray-900">
            <span>Total</span><span>{{ fmtCurrency(cart.total) }}</span>
          </div>
          <router-link to="/checkout" class="block">
            <button
              class="w-full py-3 rounded-lg text-white font-semibold text-sm"
              :style="{ backgroundColor: 'var(--shop-primary)' }"
            >Proceed to Checkout</button>
          </router-link>
          <router-link to="/products" class="block text-center text-sm text-gray-500 hover:text-gray-700">
            Continue Shopping
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useCartStore } from '../stores/cart.js'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorBanner from '../components/ErrorBanner.vue'

const cart = useCartStore()

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency', currency: 'KES', minimumFractionDigits: 0,
  }).format(Number(v) || 0)
}

let qtyTimer = {}
function onQtyChange(slug, val) {
  const qty = Math.max(1, parseInt(val) || 1)
  clearTimeout(qtyTimer[slug])
  qtyTimer[slug] = setTimeout(() => cart.updateItem(slug, qty), 600)
}

onMounted(() => cart.loadCart())
</script>
