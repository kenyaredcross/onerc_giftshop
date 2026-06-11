<template>
  <div class="p-6 space-y-4">
    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <select v-model="filters.status" class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary">
        <option value="">All Status</option>
        <option value="Pending Payment">Pending Payment</option>
        <option value="Confirmed">Confirmed</option>
        <option value="Processing">Processing</option>
        <option value="Ready for Collection">Ready for Collection</option>
        <option value="Delivered">Delivered</option>
        <option value="Cancelled">Cancelled</option>
      </select>
      <input
        v-model="filters.from_date"
        type="date"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
        placeholder="From date"
      />
      <input
        v-model="filters.to_date"
        type="date"
        class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
        placeholder="To date"
      />
      <button @click="load" class="btn-secondary">Filter</button>
    </div>

    <div v-if="error" class="card p-4 border border-red-200 bg-red-50 text-red-700 text-sm">
      {{ error }}
    </div>

    <div class="card">
      <div class="px-5 py-3 border-b border-gray-100 text-sm text-gray-500">
        {{ total }} order{{ total !== 1 ? 's' : '' }}
      </div>
      <div v-if="loading" class="p-8 flex justify-center">
        <svg class="w-6 h-6 animate-spin text-primary" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      </div>
      <DataTable
        v-else
        :columns="cols"
        :rows="rows"
        clickable
        empty-text="No orders found."
        @row-click="(r) => $router.push('/orders/' + r.order_number)"
      >
        <template #cell-status="{ row, value }">
          <StatusSelect
            :model-value="value"
            :options="nextStatuses(value)"
            :loading="updating === row.order_number"
            :disabled="updating !== null"
            @change="(s) => updateStatus(row.order_number, s)"
            @click.stop
          />
        </template>
        <template #cell-total="{ value }">
          {{ fmtCurrency(value) }}
        </template>
        <template #cell-creation="{ value }">
          {{ fmtDate(value) }}
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import DataTable from '../components/DataTable.vue'
import StatusSelect from '../components/StatusSelect.vue'
import { useApi } from '../composables/useApi.js'

const { call } = useApi()
const loading = ref(false)
const error = ref('')
const rows = ref([])
const total = ref(0)
const updating = ref(null)

const filters = reactive({ status: '', from_date: '', to_date: '' })

const cols = [
  { key: 'order_number', label: 'Order #' },
  { key: 'customer_name', label: 'Customer' },
  { key: 'total', label: 'Total' },
  { key: 'status', label: 'Status' },
  { key: 'creation', label: 'Date' },
]

const TRANSITIONS = {
  'Pending Payment': [{ value: 'Pending Payment', label: 'Pending Payment' }, { value: 'Cancelled', label: 'Cancelled' }],
  Confirmed: [
    { value: 'Confirmed', label: 'Confirmed' },
    { value: 'Processing', label: 'Processing' },
    { value: 'Cancelled', label: 'Cancelled' },
  ],
  Processing: [
    { value: 'Processing', label: 'Processing' },
    { value: 'Ready for Collection', label: 'Ready for Collection' },
    { value: 'Cancelled', label: 'Cancelled' },
  ],
  'Ready for Collection': [
    { value: 'Ready for Collection', label: 'Ready for Collection' },
    { value: 'Delivered', label: 'Delivered' },
    { value: 'Cancelled', label: 'Cancelled' },
  ],
  Delivered: [{ value: 'Delivered', label: 'Delivered' }],
  Cancelled: [{ value: 'Cancelled', label: 'Cancelled' }],
}

function nextStatuses(status) {
  return TRANSITIONS[status] || [{ value: status, label: status }]
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.status) params.status = filters.status
    if (filters.from_date) params.from_date = filters.from_date
    if (filters.to_date) params.to_date = filters.to_date
    const res = await call('onerc_giftshop.api.v1.manager.get_orders', params)
    if (res?.status === 'success') {
      rows.value = res.data || []
      total.value = res.meta?.total || rows.value.length
    } else {
      error.value = res?.message || 'Failed to load orders.'
    }
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    loading.value = false
  }
}

async function updateStatus(orderName, newStatus) {
  if (updating.value) return
  updating.value = orderName
  error.value = ''
  try {
    const res = await call('onerc_giftshop.api.v1.manager.update_order_status', {
      order_name: orderName,
      new_status: newStatus,
    })
    if (res?.status === 'success') {
      const idx = rows.value.findIndex((r) => r.order_number === orderName)
      if (idx !== -1) rows.value[idx].status = newStatus
    } else {
      error.value = res?.message || 'Status update failed.'
    }
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    updating.value = null
  }
}

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 })
    .format(Number(v) || 0)
}

function fmtDate(v) {
  if (!v) return '—'
  return new Date(v).toLocaleDateString('en-KE', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(load)
</script>
