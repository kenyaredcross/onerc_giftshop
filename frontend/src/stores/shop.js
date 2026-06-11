import { defineStore } from 'pinia'
import { useApi } from '../composables/useApi.js'

export const useShopStore = defineStore('shop', {
  state: () => {
    const s = window.__shop_settings__ || {}
    return {
      shopName: s.shop_name || 'Gift Shop',
      shopTagline: s.shop_tagline || '',
      logo: s.logo || '',
      primaryColour: s.primary_colour || '#EE2435',
      secondaryColour: s.secondary_colour || '#011E41',
      contactEmail: s.contact_email || '',
      contactPhone: s.contact_phone || '',
      enableGuestCheckout: s.enable_guest_checkout !== false,
      loaded: true,
    }
  },
  actions: {
    async loadSettings() {
      const { getShopSettings } = useApi()
      try {
        const res = await getShopSettings()
        if (res?.status === 'success') {
          const d = res.data
          this.shopName = d.shop_name || 'Gift Shop'
          this.shopTagline = d.shop_tagline || ''
          this.logo = d.logo || ''
          this.primaryColour = d.primary_colour || '#EE2435'
          this.secondaryColour = d.secondary_colour || '#011E41'
          this.contactEmail = d.contact_email || ''
          this.contactPhone = d.contact_phone || ''
          this.enableGuestCheckout = d.enable_guest_checkout !== false
          this.loaded = true
        }
      } catch (_) { /* silently keep defaults */ }
    },
  },
})
