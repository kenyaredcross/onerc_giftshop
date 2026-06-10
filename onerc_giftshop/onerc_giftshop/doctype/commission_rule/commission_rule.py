# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate, today


class CommissionRule(Document):
	def before_save(self):
		self.created_by_role = _current_shop_role()

	def validate(self):
		self._check_admin_only()
		self._check_effective_from_not_past()
		self._check_no_overlap()

	# ----------------------------------------------------------------------- #
	# private                                                                  #
	# ----------------------------------------------------------------------- #

	def _check_admin_only(self):
		if frappe.session.user == "Administrator":
			return
		if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "Shop Administrator"}):
			frappe.throw(_("Only Shop Administrators can create or edit Commission Rules."))

	def _check_effective_from_not_past(self):
		if self.is_new() and self.effective_from and getdate(self.effective_from) < getdate(today()):
			frappe.throw(_("Effective From date cannot be in the past for new Commission Rules."))

	def _check_no_overlap(self):
		"""Reject if another active rule for the same branch already covers this date range."""
		filters = {
			"branch": self.branch,
			"name": ["!=", self.name],
		}
		candidates = frappe.get_all(
			"Commission Rule",
			filters=filters,
			fields=["name", "effective_from", "effective_to"],
		)
		from_date = getdate(self.effective_from)
		to_date = getdate(self.effective_to) if self.effective_to else None

		for r in candidates:
			r_from = getdate(r.effective_from)
			r_to = getdate(r.effective_to) if r.effective_to else None

			if _ranges_overlap(from_date, to_date, r_from, r_to):
				frappe.throw(
					_("An overlapping Commission Rule ({0}) already exists for this branch and date range.").format(
						frappe.bold(r.name)
					)
				)

	# ----------------------------------------------------------------------- #
	# static / class methods                                                   #
	# ----------------------------------------------------------------------- #

	@staticmethod
	def get_rate_for_branch(branch_name, on_date=None):
		"""Return the applicable commission rate for a branch on a given date.

		Looks for a branch-specific rule first, then falls back to the global default.
		Returns None if no rule is found.
		"""
		on_date = getdate(on_date) if on_date else getdate(today())

		def _query(branch_filter):
			return frappe.db.sql(
				"""
				SELECT rate_percent
				FROM `tabCommission Rule`
				WHERE (branch = %(branch)s OR (%(branch_is_none)s AND branch IS NULL))
				  AND effective_from <= %(on_date)s
				  AND (effective_to IS NULL OR effective_to >= %(on_date)s)
				ORDER BY effective_from DESC
				LIMIT 1
				""",
				{
					"branch": branch_filter,
					"branch_is_none": 1 if branch_filter is None else 0,
					"on_date": on_date,
				},
				as_dict=True,
			)

		rows = _query(branch_name)
		if rows:
			return rows[0].rate_percent

		rows = frappe.db.sql(
			"""
			SELECT rate_percent
			FROM `tabCommission Rule`
			WHERE branch IS NULL
			  AND effective_from <= %(on_date)s
			  AND (effective_to IS NULL OR effective_to >= %(on_date)s)
			ORDER BY effective_from DESC
			LIMIT 1
			""",
			{"on_date": on_date},
			as_dict=True,
		)
		return rows[0].rate_percent if rows else None


# --------------------------------------------------------------------------- #
# module helpers                                                               #
# --------------------------------------------------------------------------- #

def _ranges_overlap(a_from, a_to, b_from, b_to):
	"""Return True if date ranges [a_from, a_to] and [b_from, b_to] overlap.

	None for *_to means open-ended (no upper bound).
	"""
	if a_to is not None and a_to < b_from:
		return False
	if b_to is not None and b_to < a_from:
		return False
	return True


def _current_shop_role():
	for role in ("Shop Administrator", "Shop Branch Manager", "Shop Finance", "Shop Region Manager"):
		if frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": role}):
			return role
	return frappe.session.user
