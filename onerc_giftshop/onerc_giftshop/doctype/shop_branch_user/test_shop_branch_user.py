# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase


EXTRA_TEST_RECORD_DEPENDENCIES = ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []


def _get_test_branch():
	return frappe.db.get_value("Shop Branch", {"is_root": 1}, "name")


class IntegrationTestShopBranchUser(IntegrationTestCase):
	def _make_test_user(self, email):
		if frappe.db.exists("User", email):
			return frappe.get_doc("User", email)
		user = frappe.get_doc({
			"doctype": "User",
			"email": email,
			"first_name": "Test",
			"last_name": "BranchUser",
			"send_welcome_email": 0,
		})
		user.append("roles", {"role": "Shop Branch Manager"})
		user.insert(ignore_permissions=True)
		return user

	def setUp(self):
		self.test_user = self._make_test_user("test_branch_user@example.com")
		frappe.db.delete("Shop Branch User", {"user": self.test_user.name})

	def test_valid_mapping_saves(self):
		branch = _get_test_branch()
		if not branch:
			self.skipTest("No root Shop Branch found; run after_install first")

		doc = frappe.get_doc({
			"doctype": "Shop Branch User",
			"user": self.test_user.name,
			"branch": branch,
			"role": "Manager",
			"is_active": 1,
		})
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Shop Branch User", doc.name))

	def test_user_without_shop_role_raises(self):
		branch = _get_test_branch()
		if not branch:
			self.skipTest("No root Shop Branch found")

		plain_user_email = "plain_user_no_role@example.com"
		if not frappe.db.exists("User", plain_user_email):
			plain_user = frappe.get_doc({
				"doctype": "User",
				"email": plain_user_email,
				"first_name": "Plain",
				"send_welcome_email": 0,
			})
			plain_user.insert(ignore_permissions=True)

		doc = frappe.get_doc({
			"doctype": "Shop Branch User",
			"user": plain_user_email,
			"branch": branch,
			"role": "Staff",
		})
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc.insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.delete("Shop Branch User", {"user": self.test_user.name})
		frappe.db.commit()
