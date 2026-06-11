<template>
  <div class="p-6 space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <select v-model="filter" class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary">
          <option value="">All Status</option>
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
          <option value="Out of Stock">Out of Stock</option>
        </select>
      </div>
      <router-link to="/products/new" class="btn-primary">+ New Product</router-link>
    </div>

    <!-- Error -->
    <div v-if="error" class="card p-4 border border-red-200 bg-red-50 text-red-700 text-sm">
      {{ error }}
    </div>

    <!-- Table -->
    <div class="card">
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
        empty-text="No product listings found."
      >
        <template #cell-status="{ value }">
          <span :class="value === 'Active' ? 'badge-active' : 'badge-inactive'">{{ value }}</span>
        </template>
        <template #cell-price="{ value }">
          {{ fmtCurrency(value) }}
        </template>
        <template #cell-actions="{ row }">
          <router-link
            v-if="row.can_edit"
            :to="'/products/' + row.name + '/edit'"
            class="btn-ghost"
          >Edit</router-link>
          <span v-else class="text-xs text-gray-400">Read-only</span>
        </template>
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import DataTable from '../components/DataTable.vue'
import { useApi } from '../composables/useApi.js'

const { call } = useApi()
const loading = ref(true)
const error = ref('')
const filter = ref('')
const allRows = ref([])

const cols = [
  { key: 'item_name', label: 'Name' },
  { key: 'slug', label: 'Slug' },
  { key: 'price', label: 'Price' },
  { key: 'status', label: 'Status' },
  { key: 'branch', label: 'Branch' },
  { key: 'actions', label: '' },
]

const rows = ref([])

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = filter.value ? { status: filter.value } : {}
    const res = await call('onerc_giftshop.api.v1.manager.get_products', params)
    if (res?.status === 'success') {
      allRows.value = res.data || []
      rows.value = allRows.value
    } else {
      error.value = res?.message || 'Failed to load products.'
    }
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    loading.value = false
  }
}

watch(filter, load)

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', {
    style: 'currency', currency: 'KES', minimumFractionDigits: 0,
  }).format(Number(v) || 0)
}

onMounted(load)
</script>
