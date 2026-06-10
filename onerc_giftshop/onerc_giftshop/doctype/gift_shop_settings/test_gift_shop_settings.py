# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase


EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestGiftShopSettings(IntegrationTestCase):
	def test_valid_settings_save(self):
		company = frappe.db.get_single_value("Global Defaults", "default_company")
		if not company:
			self.skipTest("No default company configured")

		settings = frappe.get_single("Gift Shop Settings")
		settings.shop_name = "Test Gift Shop"
		settings.default_company = company
		settings.default_currency = frappe.db.get_value("Company", company, "default_currency") or "USD"
		settings.save(ignore_permissions=True)

		reloaded = frappe.get_single("Gift Shop Settings")
		self.assertEqual(reloaded.shop_name, "Test Gift Shop")

	def test_invalid_company_raises(self):
		settings = frappe.get_single("Gift Shop Settings")
		settings.shop_name = "Test Gift Shop"
		settings.default_company = "__nonexistent_company__"
		settings.default_currency = "USD"
		with self.assertRaises(frappe.exceptions.ValidationError):
			settings.save(ignore_permissions=True)
