<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <router-link to="/account" class="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 mb-6">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Back to My Orders
    </router-link>

    <div v-if="loading" class="flex justify-center py-16">
      <LoadingSpinner size="lg" />
    </div>

    <ErrorBanner v-if="error" :message="error" class="mb-4" />

    <template v-if="order">
      <!-- Header -->
      <div class="card p-5 mb-4">
        <div class="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Order Number</p>
            <p class="text-xl font-bold text-gray-900">{{ order.order_number }}</p>
            <p class="text-sm text-gray-500 mt-1">{{ fmtDate(order.creation) }}</p>
          </div>
          <span :class="statusBadge(order.status)" class="text-sm px-3 py-1">{{ order.status }}</span>
        </div>
      </div>

      <!-- Items -->
      <div class="card p-5 mb-4">
        <h2 class="font-semibold text-gray-800 mb-3">Items</h2>
        <div class="space-y-2">
          <div
            v-for="item in order.items"
            :key="item.item_code"
            class="flex justify-between text-sm text-gray-700"
          >
            <span class="flex-1 truncate mr-2">{{ item.item_name }} × {{ item.quantity }}</span>
            <span class="flex-shrink-0">{{ fmtCurrency(item.line_total) }}</span>
          </div>
        </div>
        <div class="border-t border-gray-100 mt-3 pt-3 space-y-1">
          <div class="flex justify-between text-sm text-gray-600">
            <span>Subtotal</span><span>{{ fmtCurrency(order.subtotal) }}</span>
          </div>
          <div v-if="order.tax_amount > 0" class="flex justify-between text-sm text-gray-600">
            <span>Tax</span><span>{{ fmtCurrency(order.tax_amount) }}</span>
          </div>
          <div class="flex justify-between font-bold text-gray-900 pt-1">
            <span>Total</span><span>{{ fmtCurrency(order.total) }}</span>
          </div>
        </div>
      </div>

      <!-- Payment -->
      <div class="card p-5">
        <h2 class="font-semibold text-gray-800 mb-3">Payment Details</h2>
        <div class="text-sm text-gray-600 space-y-1">
          <p v-if="order.payment_method">Method: <span class="font-medium text-gray-900">{{ order.payment_method }}</span></p>
          <p v-if="order.shipping_address">Address: <span class="font-medium text-gray-900">{{ order.shipping_address }}</span></p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../composables/useApi.js'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorBanner from '../components/ErrorBanner.vue'

const route = useRoute()
const router = useRouter()
const { getOrder } = useApi()

const loading = ref(true)
const error = ref('')
const order = ref(null)

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 })
    .format(Number(v) || 0)
}

function fmtDate(v) {
  if (!v) return '—'
  return new Date(v).toLocaleDateString('en-KE', { day: '2-digit', month: 'short', year: 'numeric' })
}

const BADGE = {
  'Pending Payment': 'badge-pending',
  Confirmed: 'badge-confirmed',
  Processing: 'badge-processing',
  'Ready for Collection': 'badge-ready',
  Delivered: 'badge-delivered',
  Cancelled: 'badge-cancelled',
}
function statusBadge(s) { return BADGE[s] || 'badge-confirmed' }

onMounted(async () => {
  loading.value = true
  try {
    const res = await getOrder(route.params.number)
    if (res?.status === 'success') {
      order.value = res.data
    } else {
      error.value = res?.message || 'Order not found.'
      if (res?.status === 'error') router.replace('/account')
    }
  } catch (e) {
    if (e.status === 403 || e.status === 401) {
      router.replace('/account')
    } else {
      error.value = e.message || 'Failed to load order.'
    }
  } finally {
    loading.value = false
  }
})
</script>
