# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today


EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestRemittanceRecord(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		# Remittance Record links to Journal Entry, which cascades to Company →
		# Fiscal Year. Pre-seed test_objects so the generator skips that chain and
		# avoids the _Test Fiscal Year 2025 insertion conflict on this live site.
		for dt in (
			"Company", "Fiscal Year", "Cost Center", "Warehouse", "Price List",
			"Journal Entry", "Shop Branch", "Account", "Cost Center",
		):
			frappe.local.test_objects.setdefault(dt, [])
		super().setUpClass()

	def _get_root_branch(self):
		return frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")

	def _make_record(self, **kwargs):
		branch = self._get_root_branch()
		if not branch:
			self.skipTest("No root Shop Branch found; run after_install first")
		defaults = {
			"doctype": "Remittance Record",
			"branch": branch,
			"period_from": add_days(today(), -30),
			"period_to": today(),
			"gross_sales": 10000.0,
			"commission_amount": 1000.0,
			"status": "Pending",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_valid_record_saves(self):
		doc = self._make_record()
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Remittance Record", doc.name))
		doc.delete(ignore_permissions=True)

	def test_missing_branch_raises(self):
		doc = frappe.get_doc({
			"doctype": "Remittance Record",
			"period_from": add_days(today(), -30),
			"period_to": today(),
			"gross_sales": 5000.0,
			"commission_amount": 500.0,
		})
		with self.assertRaises(frappe.exceptions.MandatoryError):
			doc.insert(ignore_permissions=True)

	def test_before_submit_computes_net_payable(self):
		doc = self._make_record(gross_sales=5000.0, commission_amount=750.0)
		doc.insert(ignore_permissions=True)
		doc.before_submit()
		self.assertEqual(doc.net_payable, 4250.0)
		doc.delete(ignore_permissions=True)
