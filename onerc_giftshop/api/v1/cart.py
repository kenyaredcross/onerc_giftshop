# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, now_datetime


def _ok(data=None, message="", meta=None):
	return {"status": "success", "data": data or {}, "message": message, "meta": meta or {}}


def _err(message, data=None):
	return {"status": "error", "data": data or {}, "message": message, "meta": {}}


def _cart_to_dict(cart):
	items = []
	for item in cart.items:
		items.append({
			"listing": item.listing,
			"slug": frappe.db.get_value("Branch Product Listing", item.listing, "slug"),
			"item_code": item.item_code,
			"item_name": item.item_name,
			"quantity": item.quantity,
			"unit_price": item.unit_price,
			"line_total": item.line_total,
		})
	return {
		"name": cart.name,
		"status": cart.status,
		"subtotal": cart.subtotal,
		"tax_amount": cart.tax_amount,
		"total": cart.total,
		"items": items,
	}


def _get_open_cart():
	user = frappe.session.user
	if user and user != "Guest":
		cart_name = frappe.db.get_value(
			"Cart",
			{"customer_email": user, "status": "Open"},
			"name",
		)
	else:
		sid = frappe.session.sid
		cart_name = frappe.db.get_value(
			"Cart",
			{"session_id": sid, "status": "Open"},
			"name",
		)
	return cart_name


@frappe.whitelist(allow_guest=True)
def get_or_create_cart():
	cart_name = _get_open_cart()
	if cart_name:
		return _ok(data=_cart_to_dict(frappe.get_doc("Cart", cart_name)))

	user = frappe.session.user
	sid = frappe.session.sid
	cart = frappe.get_doc({
		"doctype": "Cart",
		"status": "Open",
		"customer_email": user if user != "Guest" else None,
		"session_id": sid,
		"expires_at": add_days(now_datetime(), 1),
	})
	cart.insert(ignore_permissions=True)
	frappe.db.commit()
	return _ok(data=_cart_to_dict(cart))


@frappe.whitelist(allow_guest=True)
def add_to_cart(listing_slug, quantity=1):
	quantity = int(quantity)
	if quantity < 1:
		return _err(_("Quantity must be at least 1."))

	listing_name = frappe.db.get_value(
		"Branch Product Listing", {"slug": listing_slug, "status": "Active"}, "name"
	)
	if not listing_name:
		return _err(_("Product not found or not available."))

	listing = frappe.get_doc("Branch Product Listing", listing_name)

	cart_name = _get_open_cart()
	if cart_name:
		cart = frappe.get_doc("Cart", cart_name)
	else:
		user = frappe.session.user
		sid = frappe.session.sid
		cart = frappe.get_doc({
			"doctype": "Cart",
			"status": "Open",
			"customer_email": user if user != "Guest" else None,
			"session_id": sid,
			"expires_at": add_days(now_datetime(), 1),
			"items": [],
		})

	# Guard against mixing branches
	if cart.items:
		existing_branch = cart.items[0].branch or frappe.db.get_value(
			"Branch Product Listing", cart.items[0].listing, "branch"
		)
		if existing_branch and existing_branch != listing.branch:
			return _err(
				_("Your cart already contains items from a different branch. Please clear your cart first.")
			)

	# Check if item already in cart
	existing_row = None
	for row in cart.items:
		if row.listing == listing_name:
			existing_row = row
			break

	if existing_row:
		existing_row.quantity += quantity
		existing_row.line_total = existing_row.quantity * existing_row.unit_price
	else:
		cart.append("items", {
			"listing": listing_name,
			"item_code": listing.item_code,
			"item_name": listing.item_name,
			"branch": listing.branch,
			"quantity": quantity,
			"unit_price": listing.price,
			"line_total": quantity * listing.price,
		})

	cart.recalculate_totals()
	cart.save(ignore_permissions=True)
	frappe.db.commit()
	return _ok(data=_cart_to_dict(cart))


@frappe.whitelist(allow_guest=True)
def update_cart_item(listing_slug, quantity):
	quantity = int(quantity)
	if quantity < 0:
		return _err(_("Quantity cannot be negative."))

	cart_name = _get_open_cart()
	if not cart_name:
		return _err(_("No open cart found."))

	cart = frappe.get_doc("Cart", cart_name)

	listing_name = frappe.db.get_value("Branch Product Listing", {"slug": listing_slug}, "name")
	if not listing_name:
		return _err(_("Product not found."))

	row_to_remove = None
	for row in cart.items:
		if row.listing == listing_name:
			if quantity == 0:
				row_to_remove = row
			else:
				row.quantity = quantity
				row.line_total = quantity * (row.unit_price or 0)
			break
	else:
		return _err(_("Item not found in cart."))

	if row_to_remove:
		cart.items.remove(row_to_remove)

	cart.recalculate_totals()
	cart.save(ignore_permissions=True)
	frappe.db.commit()
	return _ok(data=_cart_to_dict(cart))
