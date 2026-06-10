# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


class ShopBranch(Document):
	def before_save(self):
		if self.shop_slug:
			self.shop_slug = self.shop_slug.strip().lower()

	def validate(self):
		self._validate_root_uniqueness()
		self._validate_slug()
		self._check_write_permission()

	def on_update(self):
		if not self.is_root:
			remaining_roots = frappe.db.count(
				"Shop Branch", {"is_root": 1, "name": ["!=", self.name]}
			)
			if remaining_roots == 0:
				frappe.throw(
					_("At least one Shop Branch must be marked as root. Set another branch as root before removing this one.")
				)

	# ----------------------------------------------------------------------- #
	# private                                                                  #
	# ----------------------------------------------------------------------- #

	def _validate_root_uniqueness(self):
		if not self.is_root:
			return
		existing = frappe.db.get_value(
			"Shop Branch",
			{"is_root": 1, "name": ["!=", self.name]},
			"name",
		)
		if existing:
			frappe.throw(
				_("Only one Shop Branch can be the root. {0} is already marked as root.").format(
					frappe.bold(existing)
				)
			)

	def _validate_slug(self):
		if not self.shop_slug:
			frappe.throw(_("Shop Slug is required."))
		if not _SLUG_RE.match(self.shop_slug):
			frappe.throw(
				_("Shop Slug must be lowercase, start with a letter or digit, and contain only letters, digits, and hyphens. Got: {0}").format(
					frappe.bold(self.shop_slug)
				)
			)
		duplicate = frappe.db.get_value(
			"Shop Branch", {"shop_slug": self.shop_slug, "name": ["!=", self.name]}, "name"
		)
		if duplicate:
			frappe.throw(
				_("Shop Slug {0} is already used by branch {1}.").format(
					frappe.bold(self.shop_slug), frappe.bold(duplicate)
				)
			)

	def _check_write_permission(self):
		"""Branch Managers may only write their own branch record."""
		if frappe.session.user in ("Administrator", "Guest"):
			return
		if frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "Shop Administrator"}):
			return
		if frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "Shop Branch Manager"}):
			is_own = frappe.db.get_value(
				"Shop Branch", {"name": self.name, "manager": frappe.session.user}, "name"
			)
			if not is_own and not self.is_new():
				frappe.throw(_("You can only edit your own branch."))
