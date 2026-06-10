# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase


EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


def _make_branch(**kwargs):
	company = frappe.db.get_single_value("Global Defaults", "default_company") or "Test Company"
	defaults = {
		"doctype": "Shop Branch",
		"branch_name": "Test Branch",
		"shop_slug": "test-branch",
		"is_active": 1,
		"company": company,
		"cost_center": frappe.db.get_value("Cost Center", {"company": company}, "name"),
		"warehouse": frappe.db.get_value("Warehouse", {"company": company}, "name"),
		"price_list": "Standard Selling",
	}
	defaults.update(kwargs)
	return frappe.get_doc(defaults)


class IntegrationTestShopBranch(IntegrationTestCase):
	def setUp(self):
		frappe.db.delete("Shop Branch", {"shop_slug": ["in", ["test-branch", "test-hq", "bad slug"]]})

	def test_valid_branch_saves(self):
		doc = _make_branch(branch_name="Test Branch", shop_slug="test-branch")
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Shop Branch", doc.name))

	def test_invalid_slug_raises(self):
		doc = _make_branch(branch_name="Bad Slug Branch", shop_slug="Bad Slug!")
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_slug_uppercase_normalised(self):
		doc = _make_branch(branch_name="Upper Branch", shop_slug="Upper-Branch")
		doc.before_save()
		self.assertEqual(doc.shop_slug, "upper-branch")

	def test_duplicate_root_raises(self):
		first = _make_branch(branch_name="Test HQ", shop_slug="test-hq", is_root=1)
		first.insert(ignore_permissions=True)

		second = _make_branch(branch_name="Test Branch", shop_slug="test-branch", is_root=1)
		with self.assertRaises(frappe.exceptions.ValidationError):
			second.insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.delete("Shop Branch", {"shop_slug": ["in", ["test-branch", "test-hq", "upper-branch"]]})
		frappe.db.commit()
