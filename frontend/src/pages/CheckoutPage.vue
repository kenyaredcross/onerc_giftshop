<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">Checkout</h1>

    <div class="grid lg:grid-cols-2 gap-6">
      <!-- Form -->
      <div>
        <div class="card p-6">
          <h2 class="font-semibold text-gray-800 mb-4">Customer Information</h2>
          <form class="space-y-4" @submit.prevent="placeOrder">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Full Name <span class="text-red-500">*</span></label>
              <input v-model="form.fullName" required type="text"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Email Address <span class="text-red-500">*</span></label>
              <input v-model="form.email" required type="email"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number <span class="text-red-500">*</span></label>
              <input v-model="form.phone" required type="tel"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2"
                placeholder="+254 7XX XXX XXX" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Shipping Address</label>
              <textarea v-model="form.shippingAddress" rows="2"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
              <textarea v-model="form.notes" rows="2"
                class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2" />
            </div>

            <ErrorBanner v-if="error" :message="error" @dismiss="error = ''" />

            <button
              type="submit"
              :disabled="submitting"
              class="w-full py-3 rounded-lg text-white font-semibold text-sm disabled:opacity-50"
              :style="{ backgroundColor: 'var(--shop-primary)' }"
            >
              {{ submitting ? 'Processing…' : 'Place Order & Pay' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Order summary -->
      <div>
        <div class="card p-5 space-y-3">
          <h2 class="font-semibold text-gray-800">Order Summary</h2>
          <div v-for="item in cart.items" :key="item.listing" class="flex justify-between text-sm text-gray-700">
            <span class="truncate flex-1 mr-2">{{ item.item_name }} × {{ item.quantity }}</span>
            <span class="flex-shrink-0">{{ fmtCurrency(item.line_total) }}</span>
          </div>
          <div class="border-t border-gray-100 pt-3 space-y-1">
            <div class="flex justify-between text-sm text-gray-600">
              <span>Subtotal</span><span>{{ fmtCurrency(cart.subtotal) }}</span>
            </div>
            <div v-if="cart.tax_amount > 0" class="flex justify-between text-sm text-gray-600">
              <span>Tax</span><span>{{ fmtCurrency(cart.tax_amount) }}</span>
            </div>
            <div class="flex justify-between font-bold text-gray-900">
              <span>Total</span><span>{{ fmtCurrency(cart.total) }}</span>
            </div>
          </div>
          <div class="border-t border-gray-100 pt-3">
            <p class="text-xs font-medium text-gray-600 mb-1">Payment Method</p>
            <p class="text-sm font-semibold text-gray-800">M-PESA</p>
            <p class="text-xs text-gray-500 mt-1">
              You will receive a payment prompt on your phone after placing the order.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart.js'
import { useAuthStore } from '../stores/auth.js'
import { useApi } from '../composables/useApi.js'
import ErrorBanner from '../components/ErrorBanner.vue'

const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()
const { initiateCheckout } = useApi()

const submitting = ref(false)
const error = ref('')

const form = reactive({
  fullName: auth.fullName || '',
  email: auth.isGuest ? '' : auth.user,
  phone: '',
  shippingAddress: '',
  notes: '',
})

function fmtCurrency(v) {
  return new Intl.NumberFormat('en-KE', { style: 'currency', currency: 'KES', minimumFractionDigits: 0 })
    .format(Number(v) || 0)
}

async function placeOrder() {
  if (!form.fullName || !form.email || !form.phone) {
    error.value = 'Please fill in all required fields.'
    return
  }
  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)
  if (!emailOk) { error.value = 'Please enter a valid email address.'; return }

  submitting.value = true
  error.value = ''
  try {
    const res = await initiateCheckout({
      customer_name: form.fullName,
      customer_email: form.email,
      customer_phone: form.phone,
      shipping_address: form.shippingAddress,
      notes: form.notes,
    })
    if (res?.status === 'success') {
      router.push(`/checkout/processing?order=${res.data.order_number}`)
    } else {
      error.value = res?.message || 'Could not process your order. Please try again.'
    }
  } catch (e) {
    error.value = e.message || 'Network error. Please try again.'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  if (cart.isEmpty) router.replace('/cart')
  else cart.loadCart()
})
</script>
