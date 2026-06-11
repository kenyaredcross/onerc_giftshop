import { createRouter, createWebHashHistory } from 'vue-router'
import ManagerLayout from '../components/ManagerLayout.vue'
import DashboardPage from '../pages/DashboardPage.vue'
import ProductsPage from '../pages/ProductsPage.vue'
import ProductFormPage from '../pages/ProductFormPage.vue'
import OrdersPage from '../pages/OrdersPage.vue'
import OrderDetailPage from '../pages/OrderDetailPage.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      component: ManagerLayout,
      children: [
        { path: '', redirect: '/dashboard' },
        { path: '/dashboard', component: DashboardPage },
        { path: '/products', component: ProductsPage },
        { path: '/products/new', component: ProductFormPage },
        { path: '/products/:name/edit', component: ProductFormPage },
        { path: '/orders', component: OrdersPage },
        { path: '/orders/:name', component: OrderDetailPage },
      ],
    },
  ],
})

router.beforeEach((to, from, next) => {
  const user = window.__frappe_user__ || 'Guest'
  const roles = window.__frappe_roles__ || []
  if (!user || user === 'Guest') {
    window.location.href = '/login?redirect-to=' + encodeURIComponent(window.location.pathname)
    return
  }
  const isManager = roles.some((r) =>
    ['Shop Branch Manager', 'Shop Administrator', 'Shop Region Manager', 'Shop Finance'].includes(r)
  )
  if (!isManager) {
    window.location.href = '/shop?message=not_authorised'
    return
  }
  next()
})

export default router
