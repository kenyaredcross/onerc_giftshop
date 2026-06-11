<template>
  <footer class="bg-white border-t border-gray-100 mt-12">
    <div class="max-w-6xl mx-auto px-4 py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
      <div class="font-semibold text-gray-700">{{ shop.shopName }}</div>
      <div class="flex flex-col md:flex-row items-center gap-3">
        <a v-if="shop.contactEmail" :href="`mailto:${shop.contactEmail}`" class="hover:text-gray-800">
          {{ shop.contactEmail }}
        </a>
        <span v-if="shop.contactEmail && shop.contactPhone" class="hidden md:inline">·</span>
        <a v-if="shop.contactPhone" :href="`tel:${shop.contactPhone}`" class="hover:text-gray-800">
          {{ shop.contactPhone }}
        </a>
      </div>
      <div>© {{ year }} {{ shop.shopName }}</div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { useShopStore } from '../stores/shop.js'

const shop = useShopStore()
const year = computed(() => new Date().getFullYear())
</script>
