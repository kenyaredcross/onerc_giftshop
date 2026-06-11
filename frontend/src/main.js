import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import { useAuthStore } from './stores/auth.js'
import './shop.css'

const settings = window.__shop_settings__ || {}
document.documentElement.style.setProperty('--shop-primary', settings.primary_colour || '#EE2435')
document.documentElement.style.setProperty('--shop-secondary', settings.secondary_colour || '#011E41')

const pinia = createPinia()
const app = createApp(App)
app.use(pinia)

const authStore = useAuthStore()
authStore.loadSession()

app.use(router)
app.mount('#shopApp')
