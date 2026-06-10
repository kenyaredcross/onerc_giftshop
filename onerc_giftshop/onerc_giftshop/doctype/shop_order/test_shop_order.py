# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestShopOrder(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		for dt in ("Company", "Fiscal Year", "Cost Center", "Warehouse", "Price List",
				   "Customer", "Shop Branch", "Branch Product Listing", "Sales Order",
				   "Sales Invoice", "Payment Entry", "Cart"):
			frappe.local.test_objects.setdefault(dt, [])
		super().setUpClass()

	def test_autoname_format(self):
		branch = frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")
		if not branch:
			self.skipTest("No root Shop Branch — run after_install first")

		customer = frappe.db.get_value("Customer", {}, "name")
		if not customer:
			self.skipTest("No Customer records available")

		order = frappe.get_doc({
			"doctype": "Shop Order",
			"branch": branch,
			"customer": customer,
			"status": "Pending Payment",
			"total": 0,
		})
		order.insert(ignore_permissions=True)
		self.assertTrue(order.name.startswith("SO-"))
		order.delete(ignore_permissions=True)

	def test_update_status_valid_transition(self):
		branch = frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")
		if not branch:
			self.skipTest("No root Shop Branch — run after_install first")

		customer = frappe.db.get_value("Customer", {}, "name")
		if not customer:
			self.skipTest("No Customer records available")

		order = frappe.get_doc({
			"doctype": "Shop Order",
			"branch": branch,
			"customer": customer,
			"status": "Confirmed",
			"total": 0,
		})
		order.insert(ignore_permissions=True)
		order.update_status("Processing")
		self.assertEqual(frappe.db.get_value("Shop Order", order.name, "status"), "Processing")
		order.delete(ignore_permissions=True)

	def test_update_status_invalid_transition_raises(self):
		branch = frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")
		if not branch:
			self.skipTest("No root Shop Branch — run after_install first")

		customer = frappe.db.get_value("Customer", {}, "name")
		if not customer:
			self.skipTest("No Customer records available")

		order = frappe.get_doc({
			"doctype": "Shop Order",
			"branch": branch,
			"customer": customer,
			"status": "Pending Payment",
			"total": 0,
		})
		order.insert(ignore_permissions=True)
		with self.assertRaises(frappe.exceptions.ValidationError):
			order.update_status("Delivered")
		order.delete(ignore_permissions=True)
