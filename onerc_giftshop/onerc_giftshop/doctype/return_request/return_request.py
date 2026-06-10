# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, today


class ReturnRequest(Document):
	def validate(self):
		order = frappe.get_doc("Shop Order", self.shop_order)
		self.customer = order.customer
		self.branch = order.branch

		policy_days = frappe.db.get_single_value("Gift Shop Settings", "return_policy_days") or 7
		days_since = date_diff(today(), order.creation.date() if hasattr(order.creation, "date") else today())
		if days_since > policy_days:
			frappe.throw(
				_("Return window of {0} days has passed. This order was placed {1} days ago.").format(
					policy_days, days_since
				)
			)

	def on_update(self):
		if self.status == "Approved" and not self.sales_return:
			self._create_sales_return()

	def _create_sales_return(self):
		invoice_name = frappe.db.get_value("Shop Order", self.shop_order, "sales_invoice")
		if not invoice_name:
			return

		try:
			orig = frappe.get_doc("Sales Invoice", invoice_name)
			return_items = []
			for item in orig.items:
				return_items.append({
					"item_code": item.item_code,
					"qty": -abs(item.qty),
					"rate": item.rate,
					"income_account": item.income_account,
					"cost_center": item.cost_center,
				})

			ret = frappe.get_doc({
				"doctype": "Sales Invoice",
				"is_return": 1,
				"return_against": orig.name,
				"customer": orig.customer,
				"company": orig.company,
				"posting_date": today(),
				"items": return_items,
			})
			ret.insert(ignore_permissions=True)
			ret.submit()

			self.db_set("sales_return", ret.name)
			self.db_set("resolved_by", frappe.session.user)
			self.db_set("resolved_on", today())
		except Exception as e:
			frappe.log_error("Return request sales return creation failed", "Return Request")
