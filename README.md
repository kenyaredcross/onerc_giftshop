# OneRC Gift Shop

A multi-branch gift shop platform for humanitarian organisations, built on Frappe v17 + ERPNext.

Phase 1 supports a single shop (Head Office). The architecture is branch-aware from day one so Phase 2 (branch onboarding) is additive only — no refactoring needed.

## Requirements

- Frappe v17
- ERPNext
- onerc_core
- onerc_payments (optional – required for M-PESA checkout)
- onerc_sms (optional – required for SMS notifications)

## Installation

```bash
bench get-app onerc_giftshop
bench --site <site> install-app onerc_giftshop
```

`after_install` requires an ERPNext Company to be set as the default. It idempotently creates:
- HQ Shop Branch (slug: `hq`)
- Gift Shop Cost Center, Income Account, Warehouse, and Price List
- Shop roles (Shop Administrator, Shop Branch Manager, Shop Region Manager, Shop Finance)
- Item Group tree under the configured root group (default: **Gift Shop**)

## Architecture

ERPNext is the accounting backend. Every confirmed order creates:
- **Sales Order** — confirmed intent to buy
- **Sales Invoice** — payment receipt
- **Payment Entry** — records the cash/M-PESA receipt

---

## Doctypes

### Phase 1 — Backend Foundation

| Doctype | Purpose |
|---|---|
| **Gift Shop Settings** | Single — shop name, company, currency, tax template, return policy, thresholds, HQ payment account, root item group |
| **Shop Branch** | One record per physical branch. Links to ERPNext Cost Center, Warehouse, Price List. |
| **Shop Branch User** | Maps a Frappe User to a Branch with a role (Manager / Finance / Staff). |
| **Commission Rule** | Date-ranged commission rates, per-branch or global fallback. |
| **Remittance Record** | Branch-to-HQ cash settlement. Submittable; creates a Journal Entry on submit. |

### Phase 2 — E-commerce Layer

| Doctype | Purpose |
|---|---|
| **Branch Product Listing** | Activates an ERPNext Item for a specific branch with slug, price, and stock. Syncs Item Price on save. |
| **Cart** | Shopping session (Open / Checked Out / Abandoned). Contains Cart Items (child table). |
| **Cart Item** | Child of Cart — listing reference, quantity, snapshotted unit price, line total. |
| **Shop Order** | Full order lifecycle (Pending Payment → Delivered). Links to Sales Order + Sales Invoice. |
| **Shop Order Item** | Child of Shop Order — item snapshot at time of purchase. |
| **Shop Notification Template** | Per-event SMS/Email templates with `{{placeholder}}` variables. 9 default templates loaded as fixtures. |
| **Return Request** | Customer return request. Auto-creates a Sales Return (credit note) when approved. |

---

## API Endpoints

All endpoints via `/api/method/<path>`. Standard response envelope:

```json
{ "status": "success|error", "data": {}, "message": "", "meta": {} }
```

### Public Catalog (`allow_guest=True`)

| Path | Parameters | Description |
|---|---|---|
| `onerc_giftshop.api.v1.catalog.get_categories` | — | Item Group tree under `root_item_group`. Branch is never exposed. |
| `onerc_giftshop.api.v1.catalog.get_products` | `category`, `search`, `page`, `page_size` | Paginated active listings. |
| `onerc_giftshop.api.v1.catalog.get_product` | `slug` | Full detail for one product. |

### Cart (`allow_guest=True`)

| Path | Parameters | Description |
|---|---|---|
| `onerc_giftshop.api.v1.cart.get_or_create_cart` | — | Find or create open cart for this session/user. |
| `onerc_giftshop.api.v1.cart.add_to_cart` | `listing_slug`, `quantity` | Add item. Returns updated cart. |
| `onerc_giftshop.api.v1.cart.update_cart_item` | `listing_slug`, `quantity` | Update qty (0 = remove). Returns updated cart. |

### Checkout

| Path | Auth | Parameters | Description |
|---|---|---|---|
| `onerc_giftshop.api.v1.checkout.initiate_checkout` | Guest OK | `customer_email`, `customer_phone`, `customer_name`, `shipping_address`, `notes` | Cart → Shop Order + M-PESA initiation. |
| `onerc_giftshop.api.v1.checkout.payment_callback` | Guest OK | `gateway`, `payload` | Gateway webhook. Returns `{ResultCode, ResultDesc}`. |
| `onerc_giftshop.api.v1.checkout.get_order` | Required | `order_number` | Returns caller's own order only. |

### Branch Manager

Requires **Shop Branch Manager** or **Shop Administrator** role.

| Path | Parameters | Description |
|---|---|---|
| `onerc_giftshop.api.v1.manager.get_dashboard` | — | Today/week sales, pending orders, low-stock count, 5 recent orders. Scoped to branch. |
| `onerc_giftshop.api.v1.manager.get_products` | `status` | All listings with `can_edit` flag per user's branch. |
| `onerc_giftshop.api.v1.manager.update_order_status` | `order_name`, `new_status` | Advance order through valid transitions. |
| `onerc_giftshop.api.v1.manager.get_orders` | `status`, `from_date`, `to_date` | Orders scoped to manager's branch. |

---

## Order Lifecycle

Valid transitions only:

```
Pending Payment → (payment confirmed) → Confirmed
Confirmed → Processing → Ready for Collection → Delivered
Any status → Cancelled  (except Delivered or Refunded)
```

---

## Scheduled Tasks

Configured in `hooks.py` under `scheduler_events.daily`:

| Task | Description |
|---|---|
| `onerc_giftshop.tasks.check_low_stock` | SMS alert to branch manager when stock < threshold. Resets flag when replenished. |
| `onerc_giftshop.tasks.check_remittance_thresholds` | Stub — Phase 2. |
| `onerc_giftshop.tasks.expire_abandoned_carts` | Sets `status = Abandoned` on carts past `expires_at`. |

---

## Payment Gateway Configuration

Payment credentials and the active gateway are configured in **OneRC Payment Settings** (`onerc_payments` app), **not** in Gift Shop Settings.

Gift Shop Settings stores only `hq_payment_account` (Bank Account), which is passed as `recipient_account` when calling `onerc_payments.api.v1.payment.initiate_payment()`.

**Callback flow:**
1. M-PESA calls `onerc_payments.api.v1.payment.payment_callback`
2. `onerc_payments` resolves the transaction and calls `shop_order.on_payment_confirmed(amount, receipt, transaction_id)`
3. `ShopOrder.confirm_payment()` creates Sales Invoice + Payment Entry and sends notifications

---

## Roles

| Role | Access |
|---|---|
| Shop Administrator | Full access to all branches and configuration |
| Shop Branch Manager | Read all; write/create/delete only for own branch |
| Shop Region Manager | Read-only across branches |
| Shop Finance | Read and export for accounting reconciliation |

---

## Item Group Tree

Seeded by `after_install` under the root group (default: **Gift Shop** under **All Item Groups**):

- Clothing & Apparel
- Stationery & Office
- Branded Merchandise
- Books & Publications
- Food & Beverages
- Other

The root group name is configurable via **Gift Shop Settings → Root Item Group**.
