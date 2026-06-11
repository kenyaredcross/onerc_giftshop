<template>
  <div>
    <!-- Hero -->
    <section
      class="text-white px-4 py-20 text-center"
      :style="{ backgroundColor: 'var(--shop-secondary)' }"
    >
      <h1 class="text-4xl md:text-5xl font-extrabold mb-3">{{ shop.shopName }}</h1>
      <p v-if="shop.shopTagline" class="text-lg text-white/80 mb-8 max-w-xl mx-auto">
        {{ shop.shopTagline }}
      </p>
      <router-link to="/products">
        <button
          class="px-8 py-3 rounded-lg font-semibold text-white text-sm transition-all duration-150"
          :style="{ backgroundColor: 'var(--shop-primary)' }"
        >
          Browse All Products
        </button>
      </router-link>
    </section>

    <!-- Content -->
    <div class="max-w-6xl mx-auto px-4 py-10">
      <!-- Categories -->
      <div v-if="categories.length" class="flex gap-2 overflow-x-auto pb-2 scrollbar-hide mb-8">
        <CategoryPill
          v-for="cat in categories"
          :key="cat.slug"
          :name="cat.name"
          :slug="cat.slug"
          :active="false"
          @select="(s) => $router.push(`/products?category=${s}`)"
        />
      </div>

      <!-- Featured products -->
      <div v-if="loading" class="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
      <template v-else>
        <h2 class="text-xl font-bold text-gray-900 mb-5">
          {{ displayedProducts.length && showingAll ? 'All Products' : 'Featured Products' }}
        </h2>
        <ErrorBanner v-if="error" :message="error" />
        <div v-if="displayedProducts.length" class="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <ProductCard
            v-for="p in displayedProducts"
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
        <div v-else class="py-12 text-center text-gray-400">
          No products available yet.
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useShopStore } from '../stores/shop.js'
import { useCartStore } from '../stores/cart.js'
import { useToast } from '../composables/useToast.js'
import { useApi } from '../composables/useApi.js'
import ProductCard from '../components/ProductCard.vue'
import CategoryPill from '../components/CategoryPill.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import ErrorBanner from '../components/ErrorBanner.vue'

const shop = useShopStore()
const cart = useCartStore()
const toast = useToast()
const { getCategories, getProducts } = useApi()

const loading = ref(true)
const error = ref('')
const categories = ref([])
const allProducts = ref([])

const showingAll = computed(() => {
  const featured = allProducts.value.filter((p) => p.is_featured)
  return featured.length < 4
})

const displayedProducts = computed(() => {
  const featured = allProducts.value.filter((p) => p.is_featured)
  return featured.length >= 4 ? featured : allProducts.value
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [catRes, prodRes] = await Promise.all([
      getCategories(),
      getProducts({ page_size: 8 }),
    ])
    if (catRes?.status === 'success') {
      categories.value = catRes.data?.categories || []
    }
    if (prodRes?.status === 'success') {
      allProducts.value = prodRes.data || []
    } else {
      error.value = prodRes?.message || 'Failed to load products.'
    }
  } catch (e) {
    error.value = e.message || 'Network error.'
  } finally {
    loading.value = false
  }
}

async function onAddToCart({ slug }) {
  const ok = await cart.addItem(slug, 1)
  if (ok) toast.success('Added to cart!')
  else toast.error(cart.error || 'Could not add to cart.')
}

onMounted(load)
</script>
