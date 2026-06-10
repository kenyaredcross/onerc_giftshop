# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class CartItem(Document):
	def validate(self):
		self._validate_listing_active()
		self._validate_quantity()
		self._snapshot_unit_price()
		self.line_total = (self.quantity or 0) * (self.unit_price or 0)

	def _validate_listing_active(self):
		if self.listing:
			status = frappe.db.get_value("Branch Product Listing", self.listing, "status")
			if status != "Active":
				frappe.throw(
					_("Listing {0} is not active (status: {1}).").format(
						frappe.bold(self.listing), status
					)
				)

	def _validate_quantity(self):
		if (self.quantity or 0) < 1:
			frappe.throw(_("Quantity must be at least 1."))

	def _snapshot_unit_price(self):
		if not self.unit_price and self.listing:
			self.unit_price = frappe.db.get_value("Branch Product Listing", self.listing, "price") or 0
