# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestCart(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		for dt in ("Company", "Fiscal Year", "Cost Center", "Warehouse", "Price List",
				   "Customer", "Shop Branch", "Branch Product Listing"):
			frappe.local.test_objects.setdefault(dt, [])
		super().setUpClass()

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.delete("Cart", {"session_id": "test-session-cart"})

	def _make_cart(self):
		return frappe.get_doc({
			"doctype": "Cart",
			"status": "Open",
			"session_id": "test-session-cart",
		})

	def test_empty_cart_saves(self):
		cart = self._make_cart()
		cart.insert(ignore_permissions=True)
		self.assertEqual(cart.total, 0.0)

	def test_recalculate_totals_sums_items(self):
		cart = self._make_cart()
		# Manually append child rows without a real listing to test math
		cart.append("items", {"listing": None, "quantity": 2, "unit_price": 50.0, "line_total": 100.0})
		cart.recalculate_totals()
		self.assertEqual(cart.subtotal, 100.0)

	def tearDown(self):
		frappe.db.delete("Cart", {"session_id": "test-session-cart"})
		frappe.db.commit()
