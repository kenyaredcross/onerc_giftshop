# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class GiftShopSettings(Document):
	def validate(self):
		if self.default_company and not frappe.db.exists("Company", self.default_company):
			frappe.throw(_("Company {0} does not exist.").format(frappe.bold(self.default_company)))
		if self.root_item_group and not frappe.db.exists("Item Group", self.root_item_group):
			frappe.throw(_("Item Group {0} does not exist.").format(frappe.bold(self.root_item_group)))
