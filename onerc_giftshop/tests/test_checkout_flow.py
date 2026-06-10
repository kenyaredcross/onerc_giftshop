# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

"""
Integration test for the full cart → order checkout flow.

NOTE: confirm_payment() is NOT tested here because it requires a live payment
gateway response (M-PESA STK push, etc.). Automated testing of that path would
require either a test gateway or VCR-style HTTP mocking, which is out of scope
for Phase 1. Manual QA covers that flow in a staging environment.
"""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestCheckoutFlow(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		for dt in ("Company", "Fiscal Year", "Cost Center", "Warehouse", "Price List",
				   "Customer", "Shop Branch", "Branch Product Listing", "Cart",
				   "Cart Item", "Shop Order", "Sales Order"):
			frappe.local.test_objects.setdefault(dt, [])
		super().setUpClass()

	def _get_test_company(self):
		return (
			frappe.db.get_single_value("Global Defaults", "default_company")
			or frappe.db.get_value("Company", {}, "name")
		)

	def _get_hq_branch(self):
		return frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")

	def _get_or_create_test_item(self):
		code = "_Test Checkout Item"
		if frappe.db.exists("Item", code):
			return code
		item = frappe.get_doc({
			"doctype": "Item",
			"item_code": code,
			"item_name": code,
			"item_group": "All Item Groups",
			"stock_uom": "Nos",
			"is_stock_item": 1,
		})
		item.insert(ignore_permissions=True)
		return code

	def _get_or_create_listing(self, branch, item_code):
		existing = frappe.db.get_value(
			"Branch Product Listing", {"item_code": item_code, "branch": branch}, "name"
		)
		if existing:
			return frappe.get_doc("Branch Product Listing", existing)

		currency = frappe.db.get_value("Currency", {"enabled": 1}, "name") or "USD"
		listing = frappe.get_doc({
			"doctype": "Branch Product Listing",
			"branch": branch,
			"item": item_code,
			"item_code": item_code,
			"item_name": item_code,
			"slug": "checkout-test-product",
			"status": "Active",
			"price": 250.0,
			"currency": currency,
		})
		listing.insert(ignore_permissions=True)
		return listing

	def _get_or_create_customer(self):
		email = "checkout_test@example.com"
		existing = frappe.db.get_value("Customer", {"customer_name": email}, "name")
		if existing:
			return existing
		cust = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": email,
			"customer_type": "Individual",
			"customer_group": frappe.db.get_single_value("Selling Settings", "customer_group") or "All Customer Groups",
			"territory": frappe.db.get_single_value("Selling Settings", "territory") or "All Territories",
		})
		cust.insert(ignore_permissions=True)
		return cust.name

	def test_order_creation_from_cart(self):
		branch = self._get_hq_branch()
		if not branch:
			self.skipTest("No root Shop Branch — run after_install first")

		company = self._get_test_company()
		if not company:
			self.skipTest("No Company configured")

		# Ensure Gift Shop Settings has default_company
		settings = frappe.get_single("Gift Shop Settings")
		if not settings.default_company:
			self.skipTest("Gift Shop Settings.default_company not configured")

		item_code = self._get_or_create_test_item()
		listing = self._get_or_create_listing(branch, item_code)
		customer = self._get_or_create_customer()

		# Create Cart with one Cart Item
		cart = frappe.get_doc({
			"doctype": "Cart",
			"status": "Open",
			"session_id": "checkout-flow-test",
			"customer": customer,
			"customer_email": "checkout_test@example.com",
			"branch": branch,
			"items": [{
				"listing": listing.name,
				"item_code": item_code,
				"item_name": item_code,
				"branch": branch,
				"quantity": 1,
				"unit_price": listing.price,
				"line_total": listing.price,
			}],
		})
		cart.recalculate_totals()
		cart.insert(ignore_permissions=True)

		from onerc_giftshop.onerc_giftshop.doctype.shop_order.shop_order import ShopOrder
		order = ShopOrder.create_from_cart(cart.name)

		# Assertions
		self.assertIsNotNone(order)
		self.assertTrue(order.name.startswith("SO-"))
		self.assertEqual(order.status, "Pending Payment")
		self.assertIsNotNone(order.sales_order)
		self.assertTrue(frappe.db.exists("Sales Order", order.sales_order))

		cart_status = frappe.db.get_value("Cart", cart.name, "status")
		self.assertEqual(cart_status, "Checked Out")

		# Cleanup
		so = frappe.get_doc("Sales Order", order.sales_order)
		so.cancel()
		frappe.delete_doc("Sales Order", so.name, ignore_permissions=True, force=True)
		frappe.delete_doc("Shop Order", order.name, ignore_permissions=True)
		frappe.db.delete("Cart Item", {"parent": cart.name})
		frappe.delete_doc("Cart", cart.name, ignore_permissions=True)
		frappe.db.commit()
