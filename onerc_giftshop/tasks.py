# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe


def check_low_stock():
	threshold = frappe.db.get_single_value("Gift Shop Settings", "low_stock_threshold") or 5

	for name in frappe.db.get_all(
		"Branch Product Listing",
		filters={"status": "Active", "low_stock_alert_sent": 0},
		pluck="name",
	):
		doc = frappe.get_doc("Branch Product Listing", name)
		qty = doc.get_stock_qty()
		if qty < threshold:
			_send_low_stock_sms(doc)
			frappe.db.set_value("Branch Product Listing", name, "low_stock_alert_sent", 1)

	# Reset flag when stock is replenished so the next drop triggers a new alert
	for name in frappe.db.get_all(
		"Branch Product Listing",
		filters={"status": "Active", "low_stock_alert_sent": 1},
		pluck="name",
	):
		doc = frappe.get_doc("Branch Product Listing", name)
		if doc.get_stock_qty() >= threshold:
			frappe.db.set_value("Branch Product Listing", name, "low_stock_alert_sent", 0)


def check_remittance_thresholds():
	frappe.logger("onerc_giftshop").info(
		"Remittance threshold check — Phase 2 feature"
	)


def expire_abandoned_carts():
	from frappe.utils import now_datetime

	names = frappe.db.get_all(
		"Cart",
		filters={"status": "Open", "expires_at": ["<", now_datetime()]},
		pluck="name",
	)
	for name in names:
		frappe.db.set_value("Cart", name, "status", "Abandoned")

	if names:
		frappe.db.commit()
		frappe.logger("onerc_giftshop").info(
			"Expired %d abandoned cart(s)", len(names)
		)


def _send_low_stock_sms(listing):
	manager_user = frappe.db.get_value("Shop Branch", listing.branch, "manager")
	if not manager_user:
		return
	phone = frappe.db.get_value("User", manager_user, "phone") or frappe.db.get_value(
		"User", manager_user, "mobile_no"
	)
	if not phone:
		return
	try:
		from onerc_sms.utils.providers import get_active_provider, send_via_provider
		provider = get_active_provider()
		msg = (
			"Low stock alert: {item} at {branch}. Qty: {qty}.".format(
				item=listing.item_name or listing.item_code,
				branch=listing.branch,
				qty=int(listing.get_stock_qty()),
			)
		)
		send_via_provider(provider, phone, msg)
	except Exception:
		frappe.log_error("Low stock SMS failed for listing {0}".format(listing.name), "Gift Shop Tasks")
