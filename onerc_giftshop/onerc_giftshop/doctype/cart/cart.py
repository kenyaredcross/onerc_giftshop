# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Cart(Document):
	def validate(self):
		self._validate_single_branch()
		self.recalculate_totals()

	def recalculate_totals(self):
		subtotal = sum((item.line_total or 0) for item in self.items)
		self.subtotal = subtotal

		tax_amount = 0.0
		tax_template = frappe.db.get_single_value("Gift Shop Settings", "tax_template")
		if tax_template:
			rows = frappe.db.get_all(
				"Sales Taxes and Charges",
				filters={"parent": tax_template, "parenttype": "Sales Taxes and Charges Template"},
				fields=["rate"],
				limit=1,
			)
			if rows:
				tax_amount = subtotal * (rows[0].rate / 100)

		self.tax_amount = tax_amount
		self.total = subtotal + tax_amount

	def get_payment_target(self):
		unique_branches = {item.branch for item in self.items if item.branch}
		if len(unique_branches) > 1:
			return frappe.db.get_single_value("Gift Shop Settings", "hq_payment_account")
		return frappe.db.get_value("Shop Branch", self.branch, "payment_account")

	def _validate_single_branch(self):
		if not self.items:
			return
		first_branch = None
		for item in self.items:
			item_branch = item.branch or frappe.db.get_value(
				"Branch Product Listing", item.listing, "branch"
			)
			if first_branch is None:
				first_branch = item_branch
				if not self.branch:
					self.branch = first_branch
			elif item_branch != first_branch:
				frappe.throw(_("All items in your cart must be from the same branch."))
