import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth.js'
import HomePage from '../pages/HomePage.vue'
import ProductListPage from '../pages/ProductListPage.vue'
import ProductDetailPage from '../pages/ProductDetailPage.vue'
import CartPage from '../pages/CartPage.vue'
import CheckoutPage from '../pages/CheckoutPage.vue'
import PaymentProcessingPage from '../pages/PaymentProcessingPage.vue'
import OrderSuccessPage from '../pages/OrderSuccessPage.vue'
import AccountPage from '../pages/AccountPage.vue'
import CustomerOrderDetailPage from '../pages/CustomerOrderDetailPage.vue'
import LoginPage from '../pages/LoginPage.vue'

const router = createRouter({
  history: createWebHashHistory(),
  scrollBehavior() { return { top: 0 } },
  routes: [
    { path: '/', component: HomePage },
    { path: '/products', component: ProductListPage },
    { path: '/products/:slug', component: ProductDetailPage },
    { path: '/cart', component: CartPage },
    { path: '/checkout', component: CheckoutPage },
    { path: '/checkout/processing', component: PaymentProcessingPage },
    { path: '/checkout/success', component: OrderSuccessPage },
    { path: '/account', component: AccountPage, meta: { requiresAuth: true } },
    { path: '/account/orders/:number', component: CustomerOrderDetailPage, meta: { requiresAuth: true } },
    { path: '/login', component: LoginPage },
  ],
})

router.beforeEach((to) => {
  if (!to.meta.requiresAuth) return true
  const authStore = useAuthStore()
  if (authStore.isGuest) {
    return { path: '/login', query: { returnUrl: to.fullPath } }
  }
  return true
})

export default router
