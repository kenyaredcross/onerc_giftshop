import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import './manager.css'

const user = window.__frappe_user__ || 'Guest'
const roles = window.__frappe_roles__ || []

if (!user || user === 'Guest') {
  window.location.href = '/login?redirect-to=' + encodeURIComponent(window.location.pathname)
} else {
  const hasRole = roles.some((r) =>
    ['Shop Branch Manager', 'Shop Administrator', 'Shop Region Manager', 'Shop Finance'].includes(r)
  )
  if (!hasRole) {
    window.location.href = '/shop?message=not_authorised'
  } else {
    const app = createApp(App)
    app.use(createPinia())
    app.use(router)
    app.mount('#managerApp')
  }
}
