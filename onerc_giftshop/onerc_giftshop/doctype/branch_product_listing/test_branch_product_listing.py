# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


def _get_test_company():
	return (
		frappe.db.get_single_value("Global Defaults", "default_company")
		or frappe.db.get_value("Company", {}, "name")
	)


def _get_or_create_test_item():
	if frappe.db.exists("Item", "_Test Giftshop Item"):
		return "_Test Giftshop Item"
	item = frappe.get_doc({
		"doctype": "Item",
		"item_code": "_Test Giftshop Item",
		"item_name": "_Test Giftshop Item",
		"item_group": "All Item Groups",
		"stock_uom": "Nos",
		"is_stock_item": 1,
	})
	item.insert(ignore_permissions=True)
	return item.name


def _get_test_branch():
	return frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")


def _get_test_currency():
	return frappe.db.get_value("Currency", {"enabled": 1}, "name") or "USD"


def _make_listing(**kwargs):
	branch = _get_test_branch()
	if not branch:
		return None
	currency = _get_test_currency()
	item = _get_or_create_test_item()
	defaults = {
		"doctype": "Branch Product Listing",
		"branch": branch,
		"item": item,
		"item_code": item,
		"item_name": item,
		"slug": "test-product",
		"status": "Active",
		"price": 100.0,
		"currency": currency,
	}
	defaults.update(kwargs)
	return frappe.get_doc(defaults)


class IntegrationTestBranchProductListing(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		for dt in ("Company", "Fiscal Year", "Cost Center", "Warehouse", "Price List",
				   "Item", "Item Group", "Shop Branch"):
			frappe.local.test_objects.setdefault(dt, [])
		super().setUpClass()

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.delete("Branch Product Listing", {"slug": ["like", "test-%"]})

	def test_valid_listing_saves(self):
		branch = _get_test_branch()
		if not branch:
			self.skipTest("No root Shop Branch — run after_install first")
		doc = _make_listing()
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Branch Product Listing", doc.name))

	def test_slug_uniqueness_raises(self):
		branch = _get_test_branch()
		if not branch:
			self.skipTest("No root Shop Branch — run after_install first")
		first = _make_listing(slug="test-unique")
		first.insert(ignore_permissions=True)
		second = _make_listing(slug="test-unique")
		with self.assertRaises(frappe.exceptions.ValidationError):
			second.insert(ignore_permissions=True)

	def test_price_zero_raises(self):
		branch = _get_test_branch()
		if not branch:
			self.skipTest("No root Shop Branch — run after_install first")
		doc = _make_listing(price=0.0)
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc.insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.delete("Branch Product Listing", {"slug": ["like", "test-%"]})
		frappe.db.commit()
