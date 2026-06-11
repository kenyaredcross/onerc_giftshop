<template>
  <div class="flex h-screen overflow-hidden bg-light-gray">
    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen && isMobile"
      class="fixed inset-0 bg-black/50 z-20 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed top-0 left-0 h-screen z-30 flex flex-col bg-navy transition-all duration-300 select-none flex-shrink-0',
        isMobile
          ? (sidebarOpen ? 'translate-x-0 w-56' : '-translate-x-full w-56')
          : (collapsed ? 'w-14' : 'w-56'),
      ]"
    >
      <!-- Logo -->
      <div class="flex items-center h-14 px-3 border-b border-white/10 flex-shrink-0">
        <a href="/shop-manager" class="flex items-center min-w-0 flex-1">
          <div class="w-8 h-8 rounded bg-primary flex items-center justify-center text-white font-bold text-xs flex-shrink-0">GS</div>
          <div v-show="!collapsed || isMobile" class="ml-2.5 overflow-hidden">
            <p class="text-white text-sm font-bold leading-tight">Gift Shop</p>
            <p class="text-slate-400 text-xs">Manager</p>
          </div>
        </a>
        <button
          v-if="!isMobile"
          @click="collapsed = !collapsed"
          class="ml-auto text-slate-400 hover:text-white p-1 rounded transition-colors flex-shrink-0"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              :d="collapsed ? 'M9 5l7 7-7 7' : 'M15 19l-7-7 7-7'" />
          </svg>
        </button>
      </div>

      <!-- Nav -->
      <nav class="flex-1 overflow-y-auto py-3 px-2 space-y-0.5">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          @click="isMobile && (sidebarOpen = false)"
          :class="[
            'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 group relative',
            isActive(item.to)
              ? 'bg-primary text-white'
              : 'text-slate-300 hover:text-white hover:bg-white/10',
          ]"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <span v-show="!collapsed || isMobile" class="truncate">{{ item.label }}</span>
          <span
            v-if="collapsed && !isMobile"
            class="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-xs rounded
                   whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none z-50"
          >{{ item.label }}</span>
        </router-link>
      </nav>

      <!-- User footer -->
      <div class="border-t border-white/10 p-3 flex-shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
            {{ initials }}
          </div>
          <div v-show="!collapsed || isMobile" class="flex-1 min-w-0">
            <p class="text-white text-xs font-medium truncate">{{ user }}</p>
            <p class="text-slate-400 text-xs truncate">{{ primaryRole }}</p>
          </div>
          <a
            v-show="!collapsed || isMobile"
            href="/api/method/logout"
            class="text-slate-400 hover:text-white p-1 rounded transition-colors flex-shrink-0"
            title="Sign out"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
          </a>
        </div>
        <a
          v-show="!collapsed || isMobile"
          href="/app"
          class="mt-2 flex items-center gap-2 px-2 py-1.5 rounded text-slate-400 hover:text-white hover:bg-white/10 text-xs font-medium transition-colors"
          title="Open desk"
        >
          <svg class="w-3.5 h-3.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
          </svg>
          Open Desk
        </a>
      </div>
    </aside>

    <!-- Main content -->
    <div
      :class="[
        'flex flex-col flex-1 min-w-0 transition-all duration-300',
        isMobile ? 'ml-0' : (collapsed ? 'ml-14' : 'ml-56'),
      ]"
    >
      <!-- Top bar -->
      <header class="h-14 flex items-center gap-3 px-4 bg-white border-b border-gray-100 flex-shrink-0 shadow-sm">
        <button
          v-if="isMobile"
          @click="sidebarOpen = !sidebarOpen"
          class="text-gray-500 hover:text-navy p-1"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <h1 class="text-sm font-semibold text-gray-700">{{ pageTitle }}</h1>
      </header>

      <main class="flex-1 overflow-y-auto">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const collapsed = ref(false)
const sidebarOpen = ref(false)
const windowWidth = ref(window.innerWidth)
const isMobile = computed(() => windowWidth.value < 1024)

function onResize() { windowWidth.value = window.innerWidth }
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => window.removeEventListener('resize', onResize))

const user = window.__frappe_user__ || ''
const roles = window.__frappe_roles__ || []

const initials = computed(() =>
  user.split('@')[0].slice(0, 2).toUpperCase() || 'U'
)

const primaryRole = computed(() => {
  if (roles.includes('Shop Administrator')) return 'Shop Administrator'
  if (roles.includes('Shop Branch Manager')) return 'Branch Manager'
  if (roles.includes('Shop Region Manager')) return 'Region Manager'
  if (roles.includes('Shop Finance')) return 'Finance'
  return 'Manager'
})

const IconGrid = {
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>`
}
const IconBox = {
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>`
}
const IconClipboard = {
  template: `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/></svg>`
}

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: IconGrid },
  { to: '/products', label: 'Products', icon: IconBox },
  { to: '/orders', label: 'Orders', icon: IconClipboard },
]

const titles = {
  '/dashboard': 'Dashboard',
  '/products': 'Products',
  '/products/new': 'New Product',
  '/orders': 'Orders',
}

const pageTitle = computed(() => {
  if (route.path.includes('/edit')) return 'Edit Product'
  if (route.path.startsWith('/orders/')) return 'Order Detail'
  return titles[route.path] || 'Gift Shop Manager'
})

function isActive(to) {
  return route.path === to || route.path.startsWith(to + '/')
}
</script>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.15s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
