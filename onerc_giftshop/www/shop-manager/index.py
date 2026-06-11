import frappe

no_cache = 1


def get_context(context):
    context.no_cache = 1
    context.show_sidebar = 0

    user = frappe.session.user
    if not user or user == "Guest":
        frappe.local.flags.redirect_location = (
            "/login?redirect-to=/shop-manager"
        )
        raise frappe.Redirect

    context.frappe_user = user
    context.csrf_token = frappe.sessions.get_csrf_token()

    roles = frappe.get_roles(user)
    context.frappe_roles_json = frappe.as_json(roles)

    manager_roles = {
        "Shop Administrator",
        "Shop Branch Manager",
        "Shop Region Manager",
        "Shop Finance",
    }
    if not manager_roles.intersection(set(roles)):
        frappe.local.flags.redirect_location = "/shop?message=not_authorised"
        raise frappe.Redirect
