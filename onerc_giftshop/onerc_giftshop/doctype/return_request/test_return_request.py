# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestReturnRequest(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		for dt in ("Company", "Fiscal Year", "Cost Center", "Warehouse", "Price List",
				   "Customer", "Shop Branch", "Shop Order", "Sales Invoice"):
			frappe.local.test_objects.setdefault(dt, [])
		super().setUpClass()

	def _get_or_create_test_order(self):
		branch = frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")
		if not branch:
			return None
		customer = frappe.db.get_value("Customer", {}, "name")
		if not customer:
			return None
		order = frappe.get_doc({
			"doctype": "Shop Order",
			"branch": branch,
			"customer": customer,
			"status": "Delivered",
			"total": 500.0,
		})
		order.insert(ignore_permissions=True)
		return order

	def test_return_within_policy_saves(self):
		order = self._get_or_create_test_order()
		if not order:
			self.skipTest("No test data available")

		req = frappe.get_doc({
			"doctype": "Return Request",
			"shop_order": order.name,
			"reason": "Defective",
			"status": "Submitted",
		})
		req.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Return Request", req.name))
		req.delete(ignore_permissions=True)
		order.delete(ignore_permissions=True)

	def test_return_outside_policy_raises(self):
		branch = frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")
		if not branch:
			self.skipTest("No root Shop Branch")
		customer = frappe.db.get_value("Customer", {}, "name")
		if not customer:
			self.skipTest("No Customer records")

		order = frappe.get_doc({
			"doctype": "Shop Order",
			"branch": branch,
			"customer": customer,
			"status": "Delivered",
			"total": 200.0,
		})
		order.insert(ignore_permissions=True)
		# Manually set creation to a very old date
		frappe.db.set_value("Shop Order", order.name, "creation", add_days(today(), -60))

		req = frappe.get_doc({
			"doctype": "Return Request",
			"shop_order": order.name,
			"reason": "Changed Mind",
		})
		with self.assertRaises(frappe.exceptions.ValidationError):
			req.insert(ignore_permissions=True)

		order.delete(ignore_permissions=True)
		frappe.db.commit()
