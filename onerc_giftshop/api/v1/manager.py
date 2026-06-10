# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import add_days, today


def _ok(data=None, message="", meta=None):
	return {"status": "success", "data": data or {}, "message": message, "meta": meta or {}}


def _err(message, data=None):
	return {"status": "error", "data": data or {}, "message": message, "meta": {}}


def _get_manager_branch():
	roles = frappe.get_roles()
	if "Shop Administrator" in roles:
		return None  # No restriction — sees all
	return frappe.db.get_value(
		"Shop Branch User",
		{"user": frappe.session.user, "is_active": 1},
		"branch",
	)


def _branch_filter(branch):
	return {"branch": branch} if branch else {}


@frappe.whitelist()
def get_dashboard():
	frappe.has_permission("Shop Branch", throw=True)

	branch = _get_manager_branch()
	threshold = frappe.db.get_single_value("Gift Shop Settings", "low_stock_threshold") or 5
	base_filters = {"status": ["in", ["Confirmed", "Processing"]]}
	if branch:
		base_filters["branch"] = branch

	today_orders = frappe.db.get_list(
		"Shop Order",
		filters={**base_filters, "creation": [">=", today()]},
		fields=["total"],
	)
	today_sales = sum(o.total or 0 for o in today_orders)

	week_orders = frappe.db.get_list(
		"Shop Order",
		filters={**base_filters, "creation": [">=", add_days(today(), -7)]},
		fields=["total"],
	)
	week_sales = sum(o.total or 0 for o in week_orders)

	pending_orders = frappe.db.count(
		"Shop Order",
		{**base_filters},
	)

	listing_filters = {"status": "Active"}
	if branch:
		listing_filters["branch"] = branch
	listing_names = frappe.db.get_all("Branch Product Listing", filters=listing_filters, pluck="name")
	low_stock_count = 0
	for name in listing_names:
		doc = frappe.get_doc("Branch Product Listing", name)
		if doc.get_stock_qty() < threshold:
			low_stock_count += 1

	recent_order_filters = {}
	if branch:
		recent_order_filters["branch"] = branch
	recent_orders = frappe.db.get_list(
		"Shop Order",
		filters=recent_order_filters,
		fields=["order_number", "customer_name", "total", "status"],
		order_by="creation desc",
		limit=5,
	)

	return _ok(data={
		"today_sales": today_sales,
		"week_sales": week_sales,
		"pending_orders": pending_orders,
		"low_stock_count": low_stock_count,
		"recent_orders": recent_orders,
	})


@frappe.whitelist()
def get_products(status=None):
	frappe.has_permission("Shop Branch", throw=True)

	branch = _get_manager_branch()
	roles = frappe.get_roles()
	is_admin = "Shop Administrator" in roles

	filters = {}
	if branch and not is_admin:
		pass  # Branch Manager sees all listings but can_edit only their own
	if status:
		filters["status"] = status

	listings = frappe.db.get_all(
		"Branch Product Listing",
		filters=filters,
		fields=[
			"name", "item", "item_code", "item_name", "slug", "status",
			"price", "currency", "is_featured", "sort_order",
			"branch", "low_stock_alert_sent",
		],
		order_by="branch, sort_order asc",
	)

	result = []
	for l in listings:
		can_edit = is_admin or (branch is not None and l.branch == branch)
		result.append({**l, "can_edit": can_edit})

	return _ok(data=result)


@frappe.whitelist()
def update_order_status(order_name, new_status):
	frappe.has_permission("Shop Branch", throw=True)

	branch = _get_manager_branch()
	roles = frappe.get_roles()
	is_admin = "Shop Administrator" in roles

	order = frappe.get_doc("Shop Order", order_name)
	if not is_admin and branch and order.branch != branch:
		frappe.throw(_("You can only update orders for your own branch."))

	order.update_status(new_status)
	return _ok(message=_("Order status updated to {0}.").format(new_status))


@frappe.whitelist()
def get_orders(status=None, from_date=None, to_date=None):
	frappe.has_permission("Shop Branch", throw=True)

	branch = _get_manager_branch()
	filters = {}
	if branch:
		filters["branch"] = branch
	if status:
		filters["status"] = status
	if from_date:
		filters["creation"] = [">=", from_date]
	if to_date:
		filters["modified"] = ["<=", to_date]

	orders = frappe.db.get_list(
		"Shop Order",
		filters=filters,
		fields=[
			"order_number", "branch", "status", "customer_name",
			"customer_email", "total", "creation", "payment_method",
		],
		order_by="creation desc",
	)
	return _ok(data=orders, meta={"total": len(orders)})
