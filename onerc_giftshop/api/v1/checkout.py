# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def _ok(data=None, message="", meta=None):
	return {"status": "success", "data": data or {}, "message": message, "meta": meta or {}}


def _err(message, data=None):
	return {"status": "error", "data": data or {}, "message": message, "meta": {}}


@frappe.whitelist(allow_guest=True)
def initiate_checkout(
	customer_email,
	customer_phone,
	customer_name,
	shipping_address=None,
	notes=None,
):
	# 1. Find open cart
	user = frappe.session.user
	if user and user != "Guest":
		cart_name = frappe.db.get_value(
			"Cart", {"customer_email": user, "status": "Open"}, "name"
		)
	else:
		cart_name = frappe.db.get_value(
			"Cart", {"session_id": frappe.session.sid, "status": "Open"}, "name"
		)

	if not cart_name:
		return _err(_("No open cart found. Please add items to your cart first."))

	cart = frappe.get_doc("Cart", cart_name)
	if not cart.items:
		return _err(_("Your cart is empty."))

	# 2. Find or create Customer
	existing_customer = frappe.db.get_value("Customer", {"customer_name": customer_email}, "name")
	if existing_customer:
		customer = existing_customer
	else:
		cust_doc = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": customer_name or customer_email,
			"customer_type": "Individual",
			"customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups",
			"territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories",
		})
		cust_doc.insert(ignore_permissions=True)
		customer = cust_doc.name

		# Create contact with email and phone
		try:
			contact = frappe.get_doc({
				"doctype": "Contact",
				"first_name": customer_name or customer_email,
				"links": [{"link_doctype": "Customer", "link_name": customer}],
				"email_ids": [{"email_id": customer_email, "is_primary": 1}],
				"phone_nos": [{"phone": customer_phone, "is_primary_phone": 1}] if customer_phone else [],
			})
			contact.insert(ignore_permissions=True)
		except Exception:
			frappe.log_error("Contact creation failed during checkout", "Checkout")

	# 3. Update cart with customer
	frappe.db.set_value("Cart", cart_name, {
		"customer": customer,
		"customer_email": customer_email,
	})
	cart.reload()

	# 4. Create Shop Order
	from onerc_giftshop.onerc_giftshop.doctype.shop_order.shop_order import ShopOrder
	order = ShopOrder.create_from_cart(cart_name)

	frappe.db.set_value("Shop Order", order.name, {
		"customer_email": customer_email,
		"customer_phone": customer_phone,
		"shipping_address": shipping_address or "",
		"notes": notes or "",
	})
	frappe.db.commit()
	order.reload()

	# 5. Get payment target
	payment_account = cart.get_payment_target()

	# 6. Initiate payment
	payment_initiated = False
	payment_instructions = ""
	payment_result = {}

	currency = frappe.db.get_single_value("Gift Shop Settings", "default_currency") or "KES"

	try:
		from onerc_payments.api.v1.payment import initiate_payment
		result = initiate_payment(
			amount=order.total,
			currency=currency,
			direction="Inbound",
			source_app="onerc_giftshop",
			source_doctype="Shop Order",
			source_document=order.name,
			payer_name=customer_name,
			payer_phone=customer_phone,
			payer_email=customer_email,
			recipient_account=payment_account,
		)
		payment_initiated = result.get("status") in ("Pending", "Initiated")
		payment_instructions = result.get("message") or ""
		payment_result = result
	except ImportError:
		payment_instructions = _("Payment gateway not configured. Please contact the shop administrator.")
	except Exception as e:
		frappe.log_error("Payment initiation failed", "Checkout")
		payment_instructions = _("Payment gateway unavailable. Please try again or contact support.")

	if not payment_initiated and not payment_result:
		return _ok(
			data={
				"order_number": order.order_number,
				"payment_initiated": False,
				"payment_instructions": payment_instructions,
			},
			message="status=pending_payment_config",
		)

	return _ok(data={
		"order_number": order.order_number,
		"payment_initiated": payment_initiated,
		"payment_instructions": payment_instructions,
		"transaction_id": payment_result.get("transaction_id"),
	})


@frappe.whitelist(allow_guest=True)
def payment_callback(gateway=None, payload=None):
	import json

	if isinstance(payload, str):
		try:
			payload = json.loads(payload)
		except Exception:
			payload = {}

	if not payload:
		payload = {k: v for k, v in frappe.form_dict.items() if k not in ("cmd", "gateway")}

	order_ref = payload.get("order_reference") or payload.get("source_document")
	payment_ref = payload.get("payment_reference") or payload.get("receipt")

	if not order_ref:
		return {"ResultCode": 1, "ResultDesc": "No order reference in payload"}

	if not frappe.db.exists("Shop Order", order_ref):
		return {"ResultCode": 1, "ResultDesc": "Order not found"}

	try:
		order = frappe.get_doc("Shop Order", order_ref)
		order.confirm_payment(payment_ref or "", gateway or "")
	except Exception:
		frappe.log_error("Payment callback processing failed", "Checkout")
		return {"ResultCode": 1, "ResultDesc": "Processing failed"}

	return {"ResultCode": 0, "ResultDesc": "Accepted"}


@frappe.whitelist()
def get_order(order_number):
	frappe.has_permission("Shop Order", throw=True)

	order = frappe.get_doc("Shop Order", order_number)

	# Return only the requesting customer's own order
	user = frappe.session.user
	is_admin = "Shop Administrator" in frappe.get_roles() or "Shop Branch Manager" in frappe.get_roles()
	if not is_admin and order.customer_email != user:
		frappe.throw(_("You are not authorised to view this order."), frappe.PermissionError)

	items = [
		{
			"item_code": i.item_code,
			"item_name": i.item_name,
			"quantity": i.quantity,
			"unit_price": i.unit_price,
			"line_total": i.line_total,
		}
		for i in order.items
	]

	return _ok(data={
		"order_number": order.order_number,
		"status": order.status,
		"subtotal": order.subtotal,
		"tax_amount": order.tax_amount,
		"total": order.total,
		"customer_email": order.customer_email,
		"customer_phone": order.customer_phone,
		"shipping_address": order.shipping_address,
		"payment_method": order.payment_method,
		"items": items,
	})


@frappe.whitelist()
def get_customer_orders():
	user = frappe.session.user
	orders = frappe.db.get_list(
		"Shop Order",
		filters={"customer_email": user},
		fields=["order_number", "status", "total", "creation", "payment_method"],
		order_by="creation desc",
	)
	return _ok(data=orders, meta={"total": len(orders)})
