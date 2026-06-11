<template>
  <div
    class="card overflow-hidden flex flex-col cursor-pointer hover:shadow-md transition-shadow duration-200"
    @click="navigateToProduct"
  >
    <!-- Image -->
    <div class="aspect-square bg-gray-100 flex-shrink-0 overflow-hidden">
      <img
        v-if="imageUrl"
        :src="imageUrl"
        :alt="itemName"
        class="w-full h-full object-cover"
        loading="lazy"
        @error="imgError = true"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
        </svg>
      </div>
    </div>

    <!-- Content -->
    <div class="p-4 flex flex-col flex-1">
      <h3 class="font-medium text-gray-900 text-sm leading-tight line-clamp-2 flex-1">{{ itemName }}</h3>
      <div class="mt-2 flex items-center justify-between gap-2">
        <span class="font-bold text-gray-900 text-base">{{ formattedPrice }}</span>
        <span v-if="!stockAvailable" class="text-xs text-red-500 font-medium">Out of Stock</span>
      </div>
      <button
        class="mt-3 w-full py-2 px-3 rounded-lg text-sm font-semibold transition-all duration-150
               disabled:opacity-40 disabled:cursor-not-allowed text-white"
        :style="{ backgroundColor: stockAvailable ? 'var(--shop-primary)' : undefined }"
        :class="{ 'bg-gray-300': !stockAvailable }"
        :disabled="!stockAvailable || adding"
        @click.stop="handleAddToCart"
      >
        {{ adding ? 'Adding…' : (stockAvailable ? 'Add to Cart' : 'Out of Stock') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  itemCode: String,
  itemName: { type: String, required: true },
  slug: { type: String, required: true },
  price: { type: Number, default: 0 },
  currency: { type: String, default: 'KES' },
  isFeatured: Boolean,
  stockAvailable: { type: Boolean, default: true },
  imageUrl: { type: String, default: '' },
})

const emit = defineEmits(['add-to-cart'])
const router = useRouter()
const adding = ref(false)
const imgError = ref(false)

const formattedPrice = computed(() =>
  new Intl.NumberFormat('en-KE', {
    style: 'currency',
    currency: props.currency || 'KES',
    minimumFractionDigits: 0,
  }).format(props.price || 0)
)

function navigateToProduct() {
  router.push(`/products/${props.slug}`)
}

async function handleAddToCart() {
  adding.value = true
  emit('add-to-cart', { slug: props.slug, quantity: 1 })
  await new Promise((r) => setTimeout(r, 600))
  adding.value = false
}
</script>
