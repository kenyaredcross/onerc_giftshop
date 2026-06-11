<template>
  <div>
    <AppHeader />
    <main class="min-h-screen bg-light-gray">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
    <teleport to="body">
      <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
        <ToastNotification
          v-for="toast in toasts"
          :key="toast.id"
          :message="toast.message"
          :type="toast.type"
          class="pointer-events-auto"
          @dismiss="remove(toast.id)"
        />
      </div>
    </teleport>
  </div>
</template>

<script setup>
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import ToastNotification from './components/ToastNotification.vue'
import { useToast } from './composables/useToast.js'

const { toasts, remove } = useToast()
</script>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.12s ease;
}
.page-enter-from,
.page-leave-to {
  opacity: 0;
}
</style>
