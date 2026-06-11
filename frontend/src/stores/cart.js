import { defineStore } from 'pinia'
import { useApi } from '../composables/useApi.js'

export const useCartStore = defineStore('cart', {
  state: () => ({
    name: null,
    items: [],
    branch: null,
    subtotal: 0,
    tax_amount: 0,
    total: 0,
    loading: false,
    error: '',
  }),
  getters: {
    itemCount: (s) => s.items.reduce((sum, i) => sum + (i.quantity || 0), 0),
    isEmpty: (s) => s.items.length === 0,
  },
  actions: {
    _apply(data) {
      if (!data) return
      this.name = data.name || null
      this.items = data.items || []
      this.subtotal = data.subtotal || 0
      this.tax_amount = data.tax_amount || 0
      this.total = data.total || 0
    },
    async loadCart() {
      const { getOrCreateCart } = useApi()
      this.loading = true
      this.error = ''
      try {
        const res = await getOrCreateCart()
        if (res?.status === 'success') this._apply(res.data)
        else this.error = res?.message || 'Failed to load cart.'
      } catch (e) {
        this.error = e.message || 'Network error.'
      } finally {
        this.loading = false
      }
    },
    async addItem(listing_slug, quantity = 1) {
      const { addToCart } = useApi()
      this.error = ''
      try {
        const res = await addToCart(listing_slug, quantity)
        if (res?.status === 'success') this._apply(res.data)
        else { this.error = res?.message || 'Could not add item.'; return false }
        return true
      } catch (e) {
        this.error = e.message || 'Network error.'
        return false
      }
    },
    async updateItem(listing_slug, quantity) {
      const { updateCartItem } = useApi()
      this.error = ''
      try {
        const res = await updateCartItem(listing_slug, quantity)
        if (res?.status === 'success') this._apply(res.data)
        else this.error = res?.message || 'Could not update cart.'
      } catch (e) {
        this.error = e.message || 'Network error.'
      }
    },
    clearCart() {
      this.name = null
      this.items = []
      this.subtotal = 0
      this.tax_amount = 0
      this.total = 0
    },
  },
})
