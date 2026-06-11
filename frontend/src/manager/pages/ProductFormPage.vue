<template>
  <div class="p-6 max-w-2xl">
    <div class="flex items-center gap-3 mb-6">
      <button @click="$router.push('/products')" class="btn-ghost">
        <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Back
      </button>
      <h2 class="font-semibold text-gray-800">{{ isNew ? 'New Product Listing' : 'Edit Listing' }}</h2>
    </div>

    <div v-if="loadError" class="card p-4 border border-red-200 bg-red-50 text-red-700 text-sm mb-4">
      {{ loadError }}
    </div>

    <div v-if="loading" class="card p-8 flex justify-center">
      <svg class="w-6 h-6 animate-spin text-primary" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
      </svg>
    </div>

    <form v-else class="card p-6 space-y-4" @submit.prevent="save">
      <!-- Item Code -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Item Code</label>
        <input
          v-model="form.item_code"
          type="text"
          required
          :readonly="!isNew"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary
                 read-only:bg-gray-50 read-only:text-gray-500"
          placeholder="ERPNext Item Code"
        />
      </div>

      <!-- Slug -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">URL Slug</label>
        <input
          v-model="form.slug"
          type="text"
          required
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="e.g. red-cross-tshirt"
        />
      </div>

      <!-- Price -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Price</label>
        <input
          v-model.number="form.price"
          type="number"
          min="0"
          step="0.01"
          required
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="0.00"
        />
      </div>

      <!-- Status -->
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
        <select
          v-model="form.status"
          class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
        >
          <option value="Active">Active</option>
          <option value="Inactive">Inactive</option>
          <option value="Out of Stock">Out of Stock</option>
        </select>
      </div>

      <!-- Featured -->
      <div class="flex items-center gap-2">
        <input id="is_featured" v-model="form.is_featured" type="checkbox" class="rounded text-primary focus:ring-primary" />
        <label for="is_featured" class="text-sm text-gray-700">Featured product</label>
      </div>

      <!-- Save error -->
      <div v-if="saveError" class="p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
        {{ saveError }}
      </div>

      <div class="flex gap-3 pt-2">
        <button type="submit" :disabled="saving" class="btn-primary">
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
        <button type="button" class="btn-secondary" @click="$router.push('/products')">Cancel</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../composables/useApi.js'

const route = useRoute()
const router = useRouter()
const { call } = useApi()

const isNew = computed(() => route.path === '/products/new')
const loading = ref(false)
const saving = ref(false)
const loadError = ref('')
const saveError = ref('')

const form = ref({
  item_code: '',
  slug: '',
  price: 0,
  status: 'Active',
  is_featured: false,
})

async function loadExisting() {
  if (isNew.value) return
  loading.value = true
  loadError.value = ''
  try {
    const name = route.params.name
    const res = await call('frappe.client.get', { doctype: 'Branch Product Listing', name })
    if (res) {
      form.value.item_code = res.item_code || ''
      form.value.slug = res.slug || ''
      form.value.price = res.price || 0
      form.value.status = res.status || 'Active'
      form.value.is_featured = !!res.is_featured
    }
  } catch (e) {
    loadError.value = e.message || 'Failed to load product.'
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  saveError.value = ''
  try {
    if (isNew.value) {
      await call('frappe.client.insert', {
        doc: { doctype: 'Branch Product Listing', ...form.value },
      })
    } else {
      await call('frappe.client.set_value', {
        doctype: 'Branch Product Listing',
        name: route.params.name,
        fieldname: {
          slug: form.value.slug,
          price: form.value.price,
          status: form.value.status,
          is_featured: form.value.is_featured ? 1 : 0,
        },
      })
    }
    router.push('/products')
  } catch (e) {
    saveError.value = e.message || 'Save failed.'
  } finally {
    saving.value = false
  }
}

onMounted(loadExisting)
</script>
