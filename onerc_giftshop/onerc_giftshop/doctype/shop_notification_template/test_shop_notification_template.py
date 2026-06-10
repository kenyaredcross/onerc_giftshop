# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase

EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestShopNotificationTemplate(IntegrationTestCase):
	def setUp(self):
		frappe.db.delete("Shop Notification Template", {"template_name": ["like", "_Test%"]})

	def test_valid_sms_template_saves(self):
		doc = frappe.get_doc({
			"doctype": "Shop Notification Template",
			"template_name": "_Test SMS Template",
			"event": "order_confirmed",
			"channel": "SMS",
			"sms_template": "Order {{order_number}} confirmed.",
		})
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Shop Notification Template", "_Test SMS Template"))

	def test_missing_sms_template_raises(self):
		doc = frappe.get_doc({
			"doctype": "Shop Notification Template",
			"template_name": "_Test Missing SMS",
			"event": "order_processing",
			"channel": "SMS",
		})
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_email_channel_requires_subject_and_body(self):
		doc = frappe.get_doc({
			"doctype": "Shop Notification Template",
			"template_name": "_Test Email No Body",
			"event": "order_confirmed",
			"channel": "Email",
			"email_subject": "Hello",
		})
		with self.assertRaises(frappe.exceptions.ValidationError):
			doc.insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.delete("Shop Notification Template", {"template_name": ["like", "_Test%"]})
		frappe.db.commit()
