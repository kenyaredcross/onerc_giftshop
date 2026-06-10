# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def after_install():
	logger = frappe.logger("onerc_giftshop.setup")
	logger.info("onerc_giftshop: running after_install setup")

	company = _get_default_company()
	if not company:
		frappe.log_error("onerc_giftshop after_install: no default company found", "Setup")
		frappe.throw(_("Please create a Company and set it as default before installing OneRC Gift Shop."))

	cost_center = _ensure_cost_center(company)
	income_account = _ensure_income_account(company)
	warehouse = _ensure_warehouse(company)
	price_list = _ensure_price_list()
	_ensure_root_shop_branch(company, cost_center, warehouse, price_list)
	_ensure_roles()

	logger.info("onerc_giftshop: after_install complete")


# --------------------------------------------------------------------------- #
# helpers                                                                      #
# --------------------------------------------------------------------------- #

def _get_default_company():
	return frappe.db.get_default("company") or frappe.db.get_single_value("Global Defaults", "default_company")


def _ensure_cost_center(company):
	name = "Gift Shop - {}".format(_company_abbr(company))
	if frappe.db.exists("Cost Center", name):
		return name

	root = frappe.db.get_value(
		"Cost Center",
		{"company": company, "is_group": 1, "parent_cost_center": ["is", "not set"]},
		"name",
	)
	if not root:
		root = frappe.db.get_value("Cost Center", {"company": company, "is_group": 1}, "name")

	doc = frappe.get_doc({
		"doctype": "Cost Center",
		"cost_center_name": "Gift Shop",
		"company": company,
		"parent_cost_center": root,
		"is_group": 0,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


def _ensure_income_account(company):
	name = "Gift Shop Revenue - {}".format(_company_abbr(company))
	if frappe.db.exists("Account", name):
		return name

	income_root = frappe.db.get_value(
		"Account",
		{"company": company, "root_type": "Income", "is_group": 1, "parent_account": ["is", "not set"]},
		"name",
	)
	if not income_root:
		income_root = frappe.db.get_value(
			"Account",
			{"company": company, "root_type": "Income", "is_group": 1},
			"name",
		)

	doc = frappe.get_doc({
		"doctype": "Account",
		"account_name": "Gift Shop Revenue",
		"company": company,
		"parent_account": income_root,
		"root_type": "Income",
		"account_type": "Income Account",
		"is_group": 0,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


def _ensure_warehouse(company):
	if frappe.db.exists("Warehouse", {"warehouse_name": "HQ Stockroom", "company": company}):
		return frappe.db.get_value("Warehouse", {"warehouse_name": "HQ Stockroom", "company": company}, "name")

	doc = frappe.get_doc({
		"doctype": "Warehouse",
		"warehouse_name": "HQ Stockroom",
		"company": company,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


def _ensure_price_list():
	if frappe.db.exists("Price List", "HQ Standard"):
		return "HQ Standard"

	currency = frappe.db.get_single_value("System Settings", "currency") or "USD"
	doc = frappe.get_doc({
		"doctype": "Price List",
		"price_list_name": "HQ Standard",
		"currency": currency,
		"selling": 1,
		"buying": 0,
		"enabled": 1,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


def _ensure_root_shop_branch(company, cost_center, warehouse, price_list):
	if frappe.db.exists("Shop Branch", {"is_root": 1}):
		return

	branch_name = company
	doc = frappe.get_doc({
		"doctype": "Shop Branch",
		"branch_name": branch_name,
		"is_root": 1,
		"is_active": 1,
		"shop_slug": "hq",
		"company": company,
		"cost_center": cost_center,
		"warehouse": warehouse,
		"price_list": price_list,
	})
	doc.insert(ignore_permissions=True)
	frappe.db.commit()


def _ensure_roles():
	roles = [
		"Shop Administrator",
		"Shop Branch Manager",
		"Shop Region Manager",
		"Shop Finance",
	]
	for role_name in roles:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)
	frappe.db.commit()


def _company_abbr(company):
	return frappe.db.get_value("Company", company, "abbr") or company[:3].upper()
