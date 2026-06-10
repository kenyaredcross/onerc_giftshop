# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase


EXTRA_TEST_RECORD_DEPENDENCIES = []
# Shop Branch links to Company/Cost Center/Warehouse/Price List. Frappe's generator
# would cascade into ERPNext's Fiscal Year fixture, which conflicts with the real
# 2025 fiscal year on this site. Declare them as ignored so setUp handles its own data.
IGNORE_TEST_RECORD_DEPENDENCIES = ["Company", "Cost Center", "Warehouse", "Price List"]


def _get_test_company():
	"""Return any available Company, preferring the configured default."""
	return (
		frappe.db.get_single_value("Global Defaults", "default_company")
		or frappe.db.get_value("Company", {}, "name")
	)


def _make_branch(**kwargs):
	company = _get_test_company()
	cost_center = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
	warehouse = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
	price_list = frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name") or "Standard Selling"
	defaults = {
		"doctype": "Shop Branch",
		"branch_name": "Test Branch",
		"shop_slug": "test-branch",
		"is_active": 1,
		"company": company,
		"cost_center": cost_center,
		"warehouse": warehouse,
		"price_list": price_list,
	}
	defaults.update(kwargs)
	return frappe.get_doc(defaults)


class IntegrationTestShopBranch(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		# Pre-seed test_objects so the make_test_records generator skips ERPNext
		# fixture chains that conflict with the real 2025 fiscal year on this site.
		for dt in ("Company", "Fiscal Year", "Cost Center", "Warehouse", "Price List"):
			frappe.local.test_objects.setdefault(dt, [])
		super().setUpClass()

	def setUp(self):
		frappe.db.delete("Shop Branch", {"shop_slug": ["in", ["test-branch", "test-hq", "upper-branch"]]})

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
