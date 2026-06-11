function getCsrf() {
  return (
    window.__csrf_token__ ||
    document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
    ''
  )
}

async function _call(method, args = {}) {
  const res = await fetch(`/api/method/${method}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': getCsrf(),
      Accept: 'application/json',
    },
    body: JSON.stringify(args),
  })

  const json = await res.json().catch(() => ({}))

  if (!res.ok) {
    if (res.status === 403 || res.status === 401) {
      throw Object.assign(new Error('Not authorised'), { status: res.status })
    }
    throw new Error(_extractMessage(json) || `HTTP ${res.status}`)
  }

  return json.message !== undefined ? json.message : json
}

function _extractMessage(json) {
  if (json._server_messages) {
    try {
      const msgs = JSON.parse(json._server_messages)
      return msgs.map((m) => { try { return JSON.parse(m).message } catch { return m } }).join(' ')
    } catch { /* fall through */ }
  }
  const exc = json.exception || json.exc || ''
  if (exc) {
    const last = exc.split('\n').filter(Boolean).pop() || ''
    return last.replace(/^frappe\.exceptions\.\w+:\s*/, '') || exc
  }
  return json.message || null
}

export function useApi() {
  return {
    call: _call,
    getShopSettings: () => _call('onerc_giftshop.api.v1.catalog.get_shop_settings'),
    getCategories: () => _call('onerc_giftshop.api.v1.catalog.get_categories'),
    getProducts: (params = {}) => _call('onerc_giftshop.api.v1.catalog.get_products', params),
    getProduct: (slug) => _call('onerc_giftshop.api.v1.catalog.get_product', { slug }),
    getOrCreateCart: () => _call('onerc_giftshop.api.v1.cart.get_or_create_cart'),
    addToCart: (listing_slug, quantity = 1) =>
      _call('onerc_giftshop.api.v1.cart.add_to_cart', { listing_slug, quantity }),
    updateCartItem: (listing_slug, quantity) =>
      _call('onerc_giftshop.api.v1.cart.update_cart_item', { listing_slug, quantity }),
    initiateCheckout: (data) =>
      _call('onerc_giftshop.api.v1.checkout.initiate_checkout', data),
    getOrder: (order_number) =>
      _call('onerc_giftshop.api.v1.checkout.get_order', { order_number }),
    getCustomerOrders: () =>
      _call('onerc_giftshop.api.v1.checkout.get_customer_orders'),
  }
}
