<template>
  <div class="p-6 max-w-3xl space-y-5">
    <!-- Back -->
    <button @click="$router.push('/orders')" class="btn-ghost">
      <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Back to Orders
    </button>

    <!-- Loading -->
    <div v-if="loading" class="card p-8 flex justify-center">
      <svg class="w-6 h-6 animate-spin text-primary" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
    </div>

    <div v-if="error" class="card p-4 border border-red-200 bg-red-50 text-red-700 text-sm">
      {{ error }}
    </div>

    <template v-if="order">
      <!-- Order header -->
      <div class="card p-5">
        <div class="flex items-start justify-between flex-wrap gap-3">
          <div>
            <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Order</p>
            <p class="text-xl font-bold text-gray-900">{{ order.order_number }}</p>
            <p class="text-sm text-gray-500 mt-1">{{ fmtDate(order.creation) }}</p>
          </div>
          <StatusSelect
            :model-value="order.status"
            :options="nextStatuses(order.status)"
            :loading="updating"
            @change="updateStatus"
          />
        </div>
      </div>

      <!-- Customer info -->
      <div class="card p-5 grid grid-cols-2 gap-4">
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Customer</p>
          <p class="text-sm font-medium text-gray-800">{{ order.customer_name }}</p>
          <p class="text-sm text-gray-500">{{ order.customer_email }}</p>
          <p v-if="order.customer_phone" class="text-sm text-gray-500">{{ order.customer_phone }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Payment</p>
          <p class="text-sm font-medium text-gray-800">{{ order.payment_method || 'M-PESA' }}</p>
          <p v-if="order.payment_reference" class="text-sm text-gray-500">Ref: {{ order.payment_reference }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Branch</p>
          <p class="text-sm font-medium text-gray-800">{{ order.branch }}</p>
        </div>
        <div>
          <p class="text-xs text-gray-400 uppercase tracking-wide mb-1">Total</p>
          <p class="text-lg font-bold text-gray-900">{{ fmtCurrency(order.total) }}</p>
        </div>
      </div>

      <!-- Notes -->
      <div v-if="order.notes" class="card p-5">
        <p class="text-xs text-gray-400 uppercase tracking-wide mb-2">Notes</p>
        <p class="text-sm text-gray-700">{{ order.notes }}</p>
      </div>

      <!-- Order items -->
      <div class="card">
        <div class="px-5 py-4 border-b border-gray-100">
          <h3 class="font-semibold text-gray-800">Items</h3>
        </div>
        <DataTable :columns="itemCols" :rows="order.items || []" empty-text="No items found.">
          <template #cell-line_total="{ value }">
            {{ fmtCurrency(value) }}
          </template>
          <template #cell-unit_price="{ value }">
            {{ fmtCurrency(value) }}
          </template>
        </DataTable>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import DataTable from '../components/DataTable.vue'
import StatusSelect from '../components/StatusSelect.vue'
import { useApi } from '../composables/useApi.js'

const route = useRoute()
const { call } = useApi()
const loading = ref(true)
const error = ref('')
const updating = ref(false)
const order = ref(null)

const itemCols = [
  { key: 'item_name', label: 'Item' },
  { key: 'quantity', label: 'Qty' },
  { key: 'unit_price', label: 'Unit Price' },
  { key: 'line_total', label: 'Total' },
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

async function loadOrder() {
  loading.value = true
  error.value = ''
  try {
    const name = route.params.name
    const res = await call('frappe.client.get', {
      doctype: 'Shop Order',
      name,
    })
    order.value = res || null
    if (!order.value) error.value = 'Order not found.'
  } catch (e) {
    error.value = e.message || 'Failed to load order.'
  } finally {
    loading.value = false
  }
}

async function updateStatus(newStatus) {
  if (updating.value || !order.value) return
  updating.value = true
  error.value = ''
  try {
    const res = await call('onerc_giftshop.api.v1.manager.update_order_status', {
      order_name: order.value.name,
      new_status: newStatus,
    })
    if (res?.status === 'success') {
      order.value.status = newStatus
    } else {
      error.value = res?.message || 'Status update failed.'
    }
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    updating.value = false
  }
}

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 })
    .format(Number(v) || 0)
}

function fmtDate(v) {
  if (!v) return '—'
  return new Date(v).toLocaleDateString('en-KE', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(loadOrder)
</script>
