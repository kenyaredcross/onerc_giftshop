# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ShopNotificationTemplate(Document):
	def validate(self):
		if self.channel in ("SMS", "Both") and not self.sms_template:
			frappe.throw(_("SMS Template is required when channel is {0}.").format(self.channel))
		if self.channel in ("Email", "Both"):
			if not self.email_subject:
				frappe.throw(_("Email Subject is required when channel is {0}.").format(self.channel))
			if not self.email_body:
				frappe.throw(_("Email Body is required when channel is {0}.").format(self.channel))
