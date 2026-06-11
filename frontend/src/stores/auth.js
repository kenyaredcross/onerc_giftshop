import { defineStore } from 'pinia'

function getCsrf() {
  return window.__csrf_token__ || ''
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: 'Guest',
    isGuest: true,
    fullName: '',
  }),
  actions: {
    loadSession() {
      const u = window.__frappe_user__ || 'Guest'
      this.user = u
      this.isGuest = u === 'Guest'
      this.fullName = u.includes('@') ? u.split('@')[0] : u
    },
    async logout() {
      try {
        await fetch('/api/method/logout', {
          method: 'POST',
          headers: { 'X-Frappe-CSRF-Token': getCsrf() },
        })
      } finally {
        window.location.href = '/shop'
      }
    },
  },
})
