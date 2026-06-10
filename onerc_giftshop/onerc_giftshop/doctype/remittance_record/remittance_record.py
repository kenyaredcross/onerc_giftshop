# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class RemittanceRecord(Document):
	def before_submit(self):
		self.net_payable = flt(self.gross_sales) - flt(self.commission_amount)

	def on_submit(self):
		self._check_submit_permission()
		self._create_journal_entry()

	# ----------------------------------------------------------------------- #
	# private                                                                  #
	# ----------------------------------------------------------------------- #

	def _check_submit_permission(self):
		if frappe.session.user == "Administrator":
			return
		allowed = {"Shop Administrator", "Shop Finance"}
		assigned = {
			r.role for r in frappe.get_all("Has Role", filters={"parent": frappe.session.user}, fields=["role"])
		}
		if not (allowed & assigned):
			frappe.throw(_("Only Shop Administrator or Shop Finance can submit a Remittance Record."))

	def _create_journal_entry(self):
		settings = frappe.get_single("Gift Shop Settings")
		company = settings.default_company
		if not company:
			frappe.log_error("Remittance Record: no default company in Gift Shop Settings", "Remittance")
			frappe.throw(_("Please configure a Default Company in Gift Shop Settings before submitting."))

		branch_cost_center = frappe.db.get_value("Shop Branch", self.branch, "cost_center")
		company_abbr = frappe.db.get_value("Company", company, "abbr") or ""

		revenue_account = "Gift Shop Revenue - {}".format(company_abbr)
		payable_account = frappe.db.get_value(
			"Account",
			{"company": company, "account_type": "Payable", "is_group": 0},
			"name",
		)

		if not payable_account:
			frappe.log_error("Remittance Record: no Payable account found for company", "Remittance")
			frappe.throw(_("No payable account found for company {0}. Please configure your chart of accounts.").format(company))

		je = frappe.get_doc({
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"company": company,
			"posting_date": frappe.utils.today(),
			"user_remark": _("Remittance for branch {0} ({1} to {2})").format(
				self.branch, self.period_from, self.period_to
			),
			"accounts": [
				{
					"account": revenue_account,
					"cost_center": branch_cost_center,
					"debit_in_account_currency": flt(self.net_payable),
					"credit_in_account_currency": 0,
				},
				{
					"account": payable_account,
					"credit_in_account_currency": flt(self.net_payable),
					"debit_in_account_currency": 0,
				},
			],
		})
		je.insert(ignore_permissions=True)
		je.submit()

		frappe.db.set_value("Remittance Record", self.name, "journal_entry", je.name)
