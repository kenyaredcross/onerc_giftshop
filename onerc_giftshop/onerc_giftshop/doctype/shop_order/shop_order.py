# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, generate_hash, now_datetime, today


_VALID_TRANSITIONS = {
	"Confirmed": ["Processing"],
	"Processing": ["Ready for Collection"],
	"Ready for Collection": ["Delivered"],
}


class ShopOrder(Document):
	def autoname(self):
		self.name = (
			"SO-"
			+ now_datetime().strftime("%Y%m%d")
			+ "-"
			+ generate_hash(length=4).upper()
		)
		self.order_number = self.name

	# ----------------------------------------------------------------------- #
	# classmethod: create an order from an open Cart                           #
	# ----------------------------------------------------------------------- #

	@classmethod
	def create_from_cart(cls, cart_name):
		cart = frappe.get_doc("Cart", cart_name)
		if cart.status != "Open":
			frappe.throw(_("Cart {0} is not open.").format(cart_name))
		if not cart.items:
			frappe.throw(_("Cart is empty."))

		settings = frappe.get_single("Gift Shop Settings")
		company = settings.default_company
		if not company:
			frappe.throw(_("Default company is not configured in Gift Shop Settings."))

		customer = cart.customer or _get_or_create_customer(cart.customer_email)
		branch_name = cart.branch or cart.items[0].branch

		branch = frappe.get_doc("Shop Branch", branch_name)

		order = frappe.get_doc({
			"doctype": "Shop Order",
			"branch": branch_name,
			"cart": cart_name,
			"customer": customer,
			"customer_email": cart.customer_email,
			"status": "Pending Payment",
			"subtotal": cart.subtotal,
			"tax_amount": cart.tax_amount,
			"total": cart.total,
		})
		for ci in cart.items:
			order.append("items", {
				"listing": ci.listing,
				"item_code": ci.item_code,
				"item_name": ci.item_name,
				"quantity": ci.quantity,
				"unit_price": ci.unit_price,
				"line_total": ci.line_total,
			})
		order.insert(ignore_permissions=True)

		# Create ERPNext Sales Order
		so_items = []
		for item in order.items:
			so_items.append({
				"item_code": item.item_code,
				"qty": item.quantity,
				"rate": item.unit_price,
				"cost_center": branch.cost_center,
			})

		so = frappe.get_doc({
			"doctype": "Sales Order",
			"company": company,
			"customer": customer,
			"order_type": "Sales",
			"transaction_date": today(),
			"delivery_date": add_days(today(), 7),
			"price_list": branch.price_list,
			"currency": settings.default_currency,
			"items": so_items,
		})
		if settings.tax_template:
			so.taxes_and_charges = settings.tax_template
			so.set_taxes()
		so.insert(ignore_permissions=True)
		so.submit()

		order.db_set("sales_order", so.name)
		frappe.db.set_value("Cart", cart_name, "status", "Checked Out")
		frappe.db.commit()

		return order

	# ----------------------------------------------------------------------- #
	# called by onerc_payments._notify_source_app when payment completes       #
	# ----------------------------------------------------------------------- #

	def on_payment_confirmed(self, amount, receipt, transaction_id):
		gateway_name = (
			frappe.db.get_value("OneRC Payment Transaction", transaction_id, "gateway") or ""
			if frappe.db.exists("DocType", "OneRC Payment Transaction")
			else ""
		)
		self.confirm_payment(
			payment_reference=receipt or transaction_id,
			gateway_name=gateway_name,
		)

	# ----------------------------------------------------------------------- #

	def confirm_payment(self, payment_reference, gateway_name):
		self.payment_reference = payment_reference
		self.payment_gateway_name = gateway_name

		company = frappe.db.get_single_value("Gift Shop Settings", "default_company")

		try:
			sinv = self._create_sales_invoice(company)
			self._create_payment_entry(sinv, company, payment_reference)
			frappe.db.set_value("Shop Order", self.name, "sales_invoice", sinv.name)
		except Exception:
			frappe.log_error("Sales Invoice / Payment Entry creation failed", "Shop Order")

		frappe.db.set_value("Shop Order", self.name, {
			"status": "Confirmed",
			"payment_reference": payment_reference,
			"payment_gateway_name": gateway_name,
		})
		frappe.db.commit()

		try:
			self.reload()
			self.send_confirmation_notifications()
		except Exception:
			frappe.log_error("Confirmation notification failed", "Shop Order")

	def send_confirmation_notifications(self):
		if self.customer_phone:
			try:
				from onerc_sms.utils.providers import get_active_provider, send_via_provider
				provider = get_active_provider()
				msg = _("Order {0} confirmed. Total: {1}. Thank you!").format(
					self.order_number, self.total
				)
				send_via_provider(provider, self.customer_phone, str(msg))
			except Exception:
				frappe.log_error("SMS confirmation failed", "Shop Order")

		if self.customer_email:
			try:
				frappe.sendmail(
					recipients=[self.customer_email],
					subject=_("Your order {0} is confirmed").format(self.order_number),
					message=_("Order: {0}\nTotal: {1}").format(self.order_number, self.total),
				)
			except Exception:
				frappe.log_error("Email confirmation failed", "Shop Order")

	def update_status(self, new_status):
		current = self.status
		if new_status == "Cancelled":
			if current in ("Delivered", "Refunded"):
				frappe.throw(
					_("Cannot cancel an order with status {0}.").format(frappe.bold(current))
				)
		else:
			allowed = _VALID_TRANSITIONS.get(current, [])
			if new_status not in allowed:
				frappe.throw(
					_("Invalid status transition: {0} → {1}.").format(
						frappe.bold(current), frappe.bold(new_status)
					)
				)
		self.db_set("status", new_status)
		try:
			self.send_status_notification(new_status)
		except Exception:
			frappe.log_error("Status notification failed", "Shop Order")

	def send_status_notification(self, new_status):
		event_map = {
			"Processing": "order_processing",
			"Ready for Collection": "order_ready",
			"Shipped": "order_shipped",
			"Delivered": "order_delivered",
			"Cancelled": "order_cancelled",
		}
		event = event_map.get(new_status)
		if not event or not self.customer_phone:
			return

		tpl = frappe.db.get_value(
			"Shop Notification Template",
			{"event": event, "is_active": 1},
			["sms_template", "channel"],
			as_dict=True,
		)
		if not tpl or tpl.channel not in ("SMS", "Both"):
			return

		try:
			from onerc_sms.utils.providers import get_active_provider, send_via_provider
			msg = tpl.sms_template.replace("{{order_number}}", self.order_number or "")
			provider = get_active_provider()
			send_via_provider(provider, self.customer_phone, msg)
		except Exception:
			frappe.log_error("Status SMS failed", "Shop Order")

	# ----------------------------------------------------------------------- #
	# private accounting helpers                                               #
	# ----------------------------------------------------------------------- #

	def _create_sales_invoice(self, company):
		so = frappe.get_doc("Sales Order", self.sales_order)
		inv_items = []
		for item in so.items:
			inv_items.append({
				"item_code": item.item_code,
				"qty": item.qty,
				"rate": item.rate,
				"cost_center": item.cost_center,
				"sales_order": so.name,
				"so_detail": item.name,
			})

		sinv = frappe.get_doc({
			"doctype": "Sales Invoice",
			"customer": so.customer,
			"company": company,
			"posting_date": today(),
			"is_pos": 0,
			"items": inv_items,
			"taxes_and_charges": so.taxes_and_charges,
		})
		sinv.insert(ignore_permissions=True)
		sinv.submit()
		return sinv

	def _create_payment_entry(self, sinv, company, payment_reference):
		mode_of_payment = "M-PESA"
		if not frappe.db.exists("Mode of Payment", mode_of_payment):
			frappe.get_doc({
				"doctype": "Mode of Payment",
				"mode_of_payment": mode_of_payment,
				"type": "Electronic",
			}).insert(ignore_permissions=True)

		paid_to = frappe.db.get_value(
			"Mode of Payment Account",
			{"parent": mode_of_payment, "company": company},
			"default_account",
		)
		if not paid_to:
			branch_account = frappe.db.get_value("Shop Branch", self.branch, "payment_account")
			if branch_account:
				paid_to = frappe.db.get_value("Bank Account", branch_account, "account")
		if not paid_to:
			paid_to = frappe.db.get_value(
				"Account",
				{"company": company, "account_type": "Cash", "is_group": 0},
				"name",
			)

		if not paid_to:
			frappe.log_error("No paid_to account found for Payment Entry", "Shop Order")
			return

		pe = frappe.get_doc({
			"doctype": "Payment Entry",
			"payment_type": "Receive",
			"posting_date": today(),
			"company": company,
			"party_type": "Customer",
			"party": self.customer,
			"paid_amount": self.total,
			"received_amount": self.total,
			"paid_to": paid_to,
			"mode_of_payment": mode_of_payment,
			"reference_no": payment_reference,
			"reference_date": today(),
			"references": [{
				"reference_doctype": "Sales Invoice",
				"reference_name": sinv.name,
				"allocated_amount": self.total,
			}],
		})
		pe.insert(ignore_permissions=True)
		pe.submit()


# --------------------------------------------------------------------------- #
# module helpers                                                               #
# --------------------------------------------------------------------------- #

def _get_or_create_customer(email):
	if not email:
		frappe.throw(_("Customer email is required to create an order."))
	existing = frappe.db.get_value("Customer", {"customer_name": email}, "name")
	if existing:
		return existing
	customer = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": email,
		"customer_type": "Individual",
		"customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups",
		"territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories",
	})
	customer.insert(ignore_permissions=True)
	return customer.name
