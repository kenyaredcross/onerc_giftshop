<template>
  <div class="max-w-6xl mx-auto px-4 py-8">
    <!-- Filters row -->
    <div class="flex flex-col md:flex-row gap-3 mb-6">
      <input
        v-model="rawSearch"
        type="search"
        placeholder="Search products…"
        class="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2"
        :style="{ '--tw-ring-color': 'var(--shop-primary)' }"
      />
    </div>

    <!-- Category pills -->
    <div v-if="categories.length" class="flex gap-2 overflow-x-auto pb-3 mb-5">
      <CategoryPill name="All" slug="" :active="!selectedCategory" @select="selectCategory('')" />
      <CategoryPill
        v-for="cat in categories"
        :key="cat.slug"
        :name="cat.name"
        :slug="cat.slug"
        :active="selectedCategory === cat.slug"
        @select="selectCategory"
      />
    </div>

    <!-- Count -->
    <p class="text-sm text-gray-500 mb-4">
      <template v-if="!loading">{{ total }} product{{ total !== 1 ? 's' : '' }} found</template>
    </p>

    <!-- Grid -->
    <div class="relative min-h-48">
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60 z-10">
        <LoadingSpinner size="lg" />
      </div>
      <ErrorBanner v-if="error" :message="error" class="mb-4" />
      <div v-if="products.length" class="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <ProductCard
          v-for="p in products"
          :key="p.slug"
          :item-code="p.item_code"
          :item-name="p.item_name"
          :slug="p.slug"
          :price="p.price"
          :currency="p.currency"
          :is-featured="p.is_featured"
          :stock-available="p.stock_available"
          :image-url="p.image_url || ''"
          @add-to-cart="onAddToCart"
        />
      </div>
      <div v-else-if="!loading" class="text-center py-16 text-gray-400">
        <p class="text-lg font-medium mb-2">No products found</p>
        <button class="text-sm underline" @click="clearFilters">Clear filters</button>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-center gap-4 mt-8">
      <button
        class="text-sm font-medium px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-40"
        :disabled="currentPage === 1"
        @click="currentPage--"
      >Previous</button>
      <span class="text-sm text-gray-600">Page {{ currentPage }} of {{ totalPages }}</span>
      <button
        class="text-sm font-medium px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-40"
        :disabled="currentPage >= totalPages"
        @click="currentPage++"
      >Next</button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useToast } from '../composables/useToast.js'
import { useApi } from '../composables/useApi.js'
import ProductCard from '../components/ProductCard.vue'
import CategoryPill from '../components/CategoryPill.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorBanner from '../components/ErrorBanner.vue'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const toast = useToast()
const { getCategories, getProducts } = useApi()

const loading = ref(false)
const error = ref('')
const products = ref([])
const categories = ref([])
const rawSearch = ref('')
const searchQuery = ref('')
const selectedCategory = ref(route.query.category || '')
const currentPage = ref(1)
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / 12)))

let debounceTimer = null
watch(rawSearch, (val) => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    searchQuery.value = val
    currentPage.value = 1
  }, 400)
})

watch([selectedCategory, searchQuery, currentPage], load)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page: currentPage.value, page_size: 12 }
    if (selectedCategory.value) params.category = selectedCategory.value
    if (searchQuery.value) params.search = searchQuery.value
    const res = await getProducts(params)
    if (res?.status === 'success') {
      products.value = res.data || []
      total.value = res.meta?.total || 0
    } else {
      error.value = res?.message || 'Failed to load products.'
    }
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  const { getCategories: gc } = useApi()
  try {
    const res = await gc()
    if (res?.status === 'success') categories.value = res.data?.categories || []
  } catch (_) { /* ignore */ }
}

function selectCategory(slug) {
  selectedCategory.value = slug
  currentPage.value = 1
  router.replace({ query: slug ? { category: slug } : {} })
}

function clearFilters() {
  rawSearch.value = ''
  searchQuery.value = ''
  selectedCategory.value = ''
  currentPage.value = 1
}

async function onAddToCart({ slug }) {
  const ok = await cart.addItem(slug, 1)
  if (ok) toast.success('Added to cart!')
  else toast.error(cart.error || 'Could not add to cart.')
}

onMounted(async () => {
  await Promise.all([loadCategories(), load()])
})
</script>
