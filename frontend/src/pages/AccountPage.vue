<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">My Orders</h1>
        <p class="text-sm text-gray-500 mt-0.5">{{ auth.user }}</p>
      </div>
      <button
        class="text-sm border border-gray-300 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
        @click="auth.logout()"
      >Sign Out</button>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <LoadingSpinner size="lg" />
    </div>

    <ErrorBanner v-if="error" :message="error" class="mb-4" />

    <div v-if="!loading">
      <div v-if="orders.length" class="card overflow-hidden">
        <table class="min-w-full divide-y divide-gray-100">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order #</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr v-for="order in orders" :key="order.order_number" class="hover:bg-gray-50">
              <td class="px-4 py-3 text-sm font-mono font-medium text-gray-900">{{ order.order_number }}</td>
              <td class="px-4 py-3 text-sm text-gray-600">{{ fmtDate(order.creation) }}</td>
              <td class="px-4 py-3 text-sm text-gray-900 font-medium">{{ fmtCurrency(order.total) }}</td>
              <td class="px-4 py-3">
                <span :class="statusBadge(order.status)">{{ order.status }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <router-link
                  :to="`/account/orders/${order.order_number}`"
                  class="text-sm font-medium hover:underline"
                  :style="{ color: 'var(--shop-primary)' }"
                >View</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-16 text-gray-400">
        <p class="text-lg font-medium mb-2">No orders yet</p>
        <router-link to="/products">
          <button
            class="mt-2 px-6 py-2.5 rounded-lg text-white font-semibold text-sm"
            :style="{ backgroundColor: 'var(--shop-primary)' }"
          >Start Shopping</button>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { useApi } from '../composables/useApi.js'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorBanner from '../components/ErrorBanner.vue'

const auth = useAuthStore()
const { getCustomerOrders } = useApi()

const loading = ref(true)
const error = ref('')
const orders = ref([])

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
    const res = await getCustomerOrders()
    if (res?.status === 'success') orders.value = res.data || []
    else error.value = res?.message || 'Failed to load orders.'
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    loading.value = false
  }
})
</script>
