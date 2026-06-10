# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, today


EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestCommissionRule(IntegrationTestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.delete("Commission Rule", {"notes": "test-suite"})

	def _make_rule(self, **kwargs):
		defaults = {
			"doctype": "Commission Rule",
			"rate_percent": 10.0,
			"effective_from": add_days(today(), 1),
			"notes": "test-suite",
		}
		defaults.update(kwargs)
		return frappe.get_doc(defaults)

	def test_valid_global_rule_saves(self):
		doc = self._make_rule()
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Commission Rule", doc.name))

	def test_past_effective_from_raises(self):
		doc = self._make_rule(effective_from=add_days(today(), -5))
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_get_rate_for_branch_returns_global_fallback(self):
		doc = self._make_rule(rate_percent=15.0, effective_from=add_days(today(), 1))
		doc.insert(ignore_permissions=True)

		rate = frappe.get_doc("Commission Rule").get_rate_for_branch(
			"nonexistent_branch", on_date=add_days(today(), 2)
		)
		self.assertEqual(rate, 15.0)

	def tearDown(self):
		frappe.db.delete("Commission Rule", {"notes": "test-suite"})
		frappe.db.commit()
