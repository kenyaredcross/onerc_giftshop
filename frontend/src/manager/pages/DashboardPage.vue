<template>
  <div class="p-6 space-y-6">
    <!-- Stats -->
    <div v-if="loading" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="card p-5 animate-pulse">
        <div class="h-3 bg-gray-200 rounded w-2/3 mb-3"></div>
        <div class="h-7 bg-gray-200 rounded w-1/2"></div>
      </div>
    </div>
    <div v-else class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Today's Sales" :value="stats.today_sales" :currency="true" />
      <StatCard label="This Week" :value="stats.week_sales" :currency="true" />
      <StatCard label="Pending Orders" :value="stats.pending_orders" />
      <StatCard label="Low Stock Items" :value="stats.low_stock_count" />
    </div>

    <!-- Error -->
    <div v-if="error" class="card p-4 border border-red-200 bg-red-50 text-red-700 text-sm">
      {{ error }}
    </div>

    <!-- Recent Orders -->
    <div class="card">
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <h2 class="font-semibold text-gray-800">Recent Orders</h2>
        <router-link to="/orders" class="text-sm text-primary hover:underline">View all</router-link>
      </div>
      <DataTable
        :columns="orderColumns"
        :rows="stats.recent_orders || []"
        clickable
        @row-click="(r) => $router.push('/orders/' + r.order_number)"
      >
        <template #cell-status="{ value }">
          <span :class="statusBadge(value)">{{ value }}</span>
        </template>
        <template #cell-total="{ value }">
          {{ fmtCurrency(value) }}
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import StatCard from '../components/StatCard.vue'
import DataTable from '../components/DataTable.vue'
import { useApi } from '../composables/useApi.js'

const { call } = useApi()
const loading = ref(true)
const error = ref('')
const stats = ref({
  today_sales: 0,
  week_sales: 0,
  pending_orders: 0,
  low_stock_count: 0,
  recent_orders: [],
})

const orderColumns = [
  { key: 'order_number', label: 'Order #' },
  { key: 'customer_name', label: 'Customer' },
  { key: 'total', label: 'Total' },
  { key: 'status', label: 'Status' },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await call('onerc_giftshop.api.v1.manager.get_dashboard')
    if (res?.status === 'success') Object.assign(stats.value, res.data)
    else error.value = res?.message || 'Failed to load dashboard.'
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    loading.value = false
  }
}

function statusBadge(status) {
  const map = {
    'Pending Payment': 'badge-pending',
    Confirmed: 'badge-confirmed',
    Processing: 'badge-processing',
    'Ready for Collection': 'badge-ready',
    Delivered: 'badge-delivered',
    Cancelled: 'badge-cancelled',
  }
  return map[status] || 'badge-inactive'
}

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency', currency: 'KES', minimumFractionDigits: 0,
  }).format(Number(v) || 0)
}

onMounted(load)
</script>
