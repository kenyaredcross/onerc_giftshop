# Copyright (c) 2026, Kelvin Njenga and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


class BranchProductListing(Document):
	def validate(self):
		self._normalise_slug()
		self._validate_slug()
		self._validate_price()
		self._validate_active_branch()
		self._check_branch_ownership()

	def after_save(self):
		if self.status == "Active" and self.item_code:
			self._sync_item_price()

	def get_stock_qty(self):
		warehouse = frappe.db.get_value("Shop Branch", self.branch, "warehouse")
		if not warehouse or not self.item_code:
			return 0
		qty = frappe.db.get_value(
			"Bin",
			{"item_code": self.item_code, "warehouse": warehouse},
			"actual_qty",
		)
		return float(qty or 0)

	# ----------------------------------------------------------------------- #

	def _normalise_slug(self):
		if self.slug:
			self.slug = self.slug.strip().lower()

	def _validate_slug(self):
		if not self.slug:
			frappe.throw(_("Slug is required."))
		if not _SLUG_RE.match(self.slug):
			frappe.throw(
				_("Slug must be lowercase, start with a letter or digit, and contain only letters, digits, and hyphens. Got: {0}").format(
					frappe.bold(self.slug)
				)
			)
		duplicate = frappe.db.get_value(
			"Branch Product Listing",
			{"slug": self.slug, "name": ["!=", self.name or ""]},
			"name",
		)
		if duplicate:
			frappe.throw(
				_("Slug {0} is already used by another listing.").format(frappe.bold(self.slug))
			)

	def _validate_price(self):
		if self.price is not None and self.price <= 0:
			frappe.throw(_("Price must be greater than zero."))

	def _validate_active_branch(self):
		if self.branch:
			is_active = frappe.db.get_value("Shop Branch", self.branch, "is_active")
			if not is_active:
				frappe.throw(_("Branch {0} is not active.").format(frappe.bold(self.branch)))

	def _check_branch_ownership(self):
		if frappe.session.user == "Administrator":
			return
		roles = frappe.get_roles()
		if "Shop Administrator" in roles:
			return
		user_branch = frappe.db.get_value(
			"Shop Branch User",
			{"user": frappe.session.user, "is_active": 1},
			"branch",
		)
		if self.branch != user_branch:
			frappe.throw(_("You can only manage products for your own branch."))

	def _sync_item_price(self):
		price_list = frappe.db.get_value("Shop Branch", self.branch, "price_list")
		if not price_list:
			return
		currency = self.currency or frappe.db.get_single_value("Gift Shop Settings", "default_currency")
		existing = frappe.db.get_value(
			"Item Price",
			{"item_code": self.item_code, "price_list": price_list},
			"name",
		)
		if existing:
			frappe.db.set_value("Item Price", existing, {
				"price_list_rate": self.price,
				"currency": currency,
			})
		else:
			frappe.get_doc({
				"doctype": "Item Price",
				"item_code": self.item_code,
				"price_list": price_list,
				"price_list_rate": self.price,
				"currency": currency,
				"selling": 1,
			}).insert(ignore_permissions=True)
