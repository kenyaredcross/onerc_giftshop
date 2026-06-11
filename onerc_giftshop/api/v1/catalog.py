# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def _ok(data=None, message="", meta=None):
	return {"status": "success", "data": data or {}, "message": message, "meta": meta or {}}


def _err(message, data=None):
	return {"status": "error", "data": data or {}, "message": message, "meta": {}}


def _to_slug(name):
	return name.lower().replace(" & ", "-").replace(" ", "-").replace("&", "-")


@frappe.whitelist(allow_guest=True)
def get_shop_settings():
	settings = frappe.get_single("Gift Shop Settings")
	return _ok(data={
		"shop_name": settings.shop_name or "Gift Shop",
		"shop_tagline": settings.shop_tagline or "",
		"logo": settings.logo or "",
		"primary_colour": settings.primary_colour or "#EE2435",
		"secondary_colour": settings.secondary_colour or "#011E41",
		"contact_email": settings.contact_email or "",
		"contact_phone": settings.contact_phone or "",
		"enable_guest_checkout": bool(settings.enable_guest_checkout),
	})


@frappe.whitelist(allow_guest=True)
def get_categories():
	root = frappe.db.get_single_value("Gift Shop Settings", "root_item_group") or "Gift Shop"

	def _build_tree(parent):
		children = frappe.db.get_all(
			"Item Group",
			filters={"parent_item_group": parent},
			fields=["name", "parent_item_group", "is_group"],
			order_by="name",
		)
		result = []
		for g in children:
			result.append({
				"name": g.name,
				"slug": _to_slug(g.name),
				"parent_item_group": g.parent_item_group,
				"children": _build_tree(g.name) if g.is_group else [],
			})
		return result

	return _ok(
		data={"root": root, "categories": _build_tree(root)},
		message=_("Categories fetched"),
	)


@frappe.whitelist(allow_guest=True)
def get_products(category=None, search=None, page=1, page_size=20):
	page = max(1, int(page))
	page_size = max(1, min(int(page_size), 100))

	filters = {"status": "Active"}

	if search:
		# We'll filter in Python after fetching to support OR across fields
		pass

	listings = frappe.db.get_all(
		"Branch Product Listing",
		filters=filters,
		fields=[
			"name", "item", "item_code", "item_name", "slug", "price", "currency",
			"is_featured", "branch_description", "branch",
		],
		order_by="is_featured desc, sort_order asc, creation desc",
	)

	# Apply category filter
	if category:
		item_group_names = _get_item_group_and_descendants(category)
		filtered = []
		for l in listings:
			item_group = frappe.db.get_value("Item", l.item, "item_group") if l.item else None
			if item_group in item_group_names:
				filtered.append(l)
		listings = filtered

	# Apply search filter
	if search:
		q = search.lower()
		listings = [
			l for l in listings
			if q in (l.item_name or "").lower() or q in (l.item_code or "").lower()
		]

	total = len(listings)
	start = (page - 1) * page_size
	page_listings = listings[start: start + page_size]

	products = []
	for l in page_listings:
		doc = frappe.get_doc("Branch Product Listing", l.name)
		stock_qty = doc.get_stock_qty()
		item_group = frappe.db.get_value("Item", l.item, "item_group") if l.item else None
		products.append({
			"item_code": l.item_code,
			"item_name": l.item_name,
			"slug": l.slug,
			"price": l.price,
			"currency": l.currency,
			"is_featured": l.is_featured,
			"stock_available": stock_qty > 0,
			"short_description": (l.branch_description or "")[:160] or _get_item_description(l.item),
			"category": item_group,
		})

	return _ok(
		data=products,
		meta={"total": total, "page": page, "page_size": page_size},
	)


@frappe.whitelist(allow_guest=True)
def get_product(slug):
	name = frappe.db.get_value("Branch Product Listing", {"slug": slug, "status": "Active"}, "name")
	if not name:
		return _err(_("Product not found."))

	doc = frappe.get_doc("Branch Product Listing", name)
	stock_qty = doc.get_stock_qty()
	item_group = frappe.db.get_value("Item", doc.item, "item_group") if doc.item else None
	images = frappe.db.get_all(
		"File",
		filters={"attached_to_doctype": "Item", "attached_to_name": doc.item, "is_private": 0},
		fields=["file_url"],
	)

	return _ok(data={
		"item_code": doc.item_code,
		"item_name": doc.item_name,
		"slug": doc.slug,
		"price": doc.price,
		"currency": doc.currency,
		"is_featured": doc.is_featured,
		"stock_available": stock_qty > 0,
		"stock_qty": int(stock_qty),
		"description": doc.branch_description or _get_item_description(doc.item),
		"short_description": (doc.branch_description or "")[:160] or _get_item_description(doc.item),
		"category": item_group,
		"images": [f.file_url for f in images],
	})


def _get_item_description(item_name):
	if not item_name:
		return ""
	desc = frappe.db.get_value("Item", item_name, "description") or ""
	return (desc or "")[:160]


def _get_item_group_and_descendants(group_name):
	result = {group_name}
	children = frappe.db.get_all("Item Group", filters={"parent_item_group": group_name}, pluck="name")
	for child in children:
		result |= _get_item_group_and_descendants(child)
	return result
