<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <router-link to="/products" class="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-800 mb-6">
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      All Products
    </router-link>

    <div v-if="loading" class="flex justify-center py-20">
      <LoadingSpinner size="lg" />
    </div>

    <ErrorBanner v-if="error" :message="error" class="mb-6" />

    <div v-if="product" class="grid md:grid-cols-2 gap-8">
      <!-- Image -->
      <div class="aspect-square bg-gray-100 rounded-card overflow-hidden">
        <img
          v-if="product.images && product.images[0]"
          :src="product.images[0]"
          :alt="product.item_name"
          class="w-full h-full object-cover"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
          <svg class="w-20 h-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
        </div>
      </div>

      <!-- Details -->
      <div class="flex flex-col">
        <h1 class="text-2xl font-bold text-gray-900">{{ product.item_name }}</h1>

        <div class="mt-3 flex items-center gap-3">
          <span class="text-2xl font-bold text-gray-900">{{ formattedPrice }}</span>
          <span
            :class="product.stock_available ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'"
            class="px-2.5 py-0.5 rounded-full text-xs font-medium"
          >
            {{ product.stock_available ? `In Stock (${product.stock_qty})` : 'Out of Stock' }}
          </span>
        </div>

        <div
          v-if="product.description"
          class="mt-4 text-gray-600 text-sm leading-relaxed prose prose-sm max-w-none"
          v-html="product.description"
        />

        <!-- Add to cart -->
        <div v-if="product.stock_available" class="mt-6 flex items-center gap-3">
          <input
            v-model.number="quantity"
            type="number"
            min="1"
            max="99"
            class="w-20 border border-gray-300 rounded-lg px-3 py-2 text-sm text-center focus:outline-none focus:ring-2"
          />
          <button
            class="flex-1 py-3 px-5 rounded-lg text-white font-semibold text-sm transition-all duration-150 disabled:opacity-50"
            :style="{ backgroundColor: 'var(--shop-primary)' }"
            :disabled="adding"
            @click="addToCart"
          >
            {{ adding ? 'Adding…' : 'Add to Cart' }}
          </button>
        </div>

        <ErrorBanner v-if="addError" :message="addError" class="mt-3" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useToast } from '../composables/useToast.js'
import { useApi } from '../composables/useApi.js'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorBanner from '../components/ErrorBanner.vue'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const toast = useToast()
const { getProduct } = useApi()

const loading = ref(true)
const error = ref('')
const addError = ref('')
const adding = ref(false)
const quantity = ref(1)
const product = ref(null)

const formattedPrice = computed(() => {
  if (!product.value) return ''
  return new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: product.value.currency || 'KES',
    minimumFractionDigits: 0,
  }).format(product.value.price || 0)
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await getProduct(route.params.slug)
    if (res?.status === 'success' && res.data?.slug) {
      product.value = res.data
    } else {
      router.replace('/products')
    }
  } catch (e) {
    error.value = e.message || 'Failed to load product.'
  } finally {
    loading.value = false
  }
}

async function addToCart() {
  adding.value = true
  addError.value = ''
  const ok = await cart.addItem(product.value.slug, quantity.value)
  if (ok) {
    toast.success('Added to cart!')
    quantity.value = 1
  } else {
    addError.value = cart.error || 'Could not add to cart.'
  }
  adding.value = false
}

onMounted(load)
</script>
