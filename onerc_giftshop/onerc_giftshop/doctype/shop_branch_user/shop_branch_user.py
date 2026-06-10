# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

_SHOP_ROLES = {
	"Shop Administrator",
	"Shop Branch Manager",
	"Shop Region Manager",
	"Shop Finance",
}

_ROLE_TO_FRAPPE_ROLE = {
	"Manager": "Shop Branch Manager",
	"Finance": "Shop Finance",
	"Staff": "Shop Branch Manager",
}


class ShopBranchUser(Document):
	def validate(self):
		self._check_unique_pair()
		self._check_user_has_shop_role()

	def on_update(self):
		self._sync_frappe_role()

	# ----------------------------------------------------------------------- #
	# private                                                                  #
	# ----------------------------------------------------------------------- #

	def _check_unique_pair(self):
		duplicate = frappe.db.get_value(
			"Shop Branch User",
			{"user": self.user, "branch": self.branch, "name": ["!=", self.name]},
			"name",
		)
		if duplicate:
			frappe.throw(
				_("User {0} is already mapped to branch {1}.").format(
					frappe.bold(self.user), frappe.bold(self.branch)
				)
			)

	def _check_user_has_shop_role(self):
		assigned = {
			r.role
			for r in frappe.get_all("Has Role", filters={"parent": self.user}, fields=["role"])
		}
		if not (_SHOP_ROLES & assigned):
			frappe.throw(
				_("User {0} must have at least one Shop role assigned before being mapped to a branch.").format(
					frappe.bold(self.user)
				)
			)

	def _sync_frappe_role(self):
		target_role = _ROLE_TO_FRAPPE_ROLE.get(self.role)
		if not target_role:
			return
		user_doc = frappe.get_doc("User", self.user)
		has_role = any(r.role == target_role for r in user_doc.roles)
		if not has_role:
			user_doc.append("roles", {"role": target_role})
			user_doc.save(ignore_permissions=True)
