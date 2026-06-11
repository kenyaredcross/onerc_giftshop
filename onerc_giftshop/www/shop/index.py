import frappe

no_cache = 1


def get_context(context):
    context.no_cache = 1
    context.show_sidebar = 0

    user = frappe.session.user
    context.frappe_user = user or "Guest"
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.frappe_roles_json = frappe.as_json(
        frappe.get_roles(user) if (user and user != "Guest") else []
    )

    try:
        settings = frappe.get_single("Gift Shop Settings")
        context.shop_name = settings.shop_name or "Gift Shop"
        context.shop_settings_json = frappe.as_json({
            "shop_name": settings.shop_name or "Gift Shop",
            "shop_tagline": settings.shop_tagline or "",
            "logo": settings.logo or "",
            "primary_colour": settings.primary_colour or "#EE2435",
            "secondary_colour": settings.secondary_colour or "#011E41",
            "contact_email": settings.contact_email or "",
            "contact_phone": settings.contact_phone or "",
            "enable_guest_checkout": bool(settings.enable_guest_checkout),
        })
    except Exception:
        context.shop_name = "Gift Shop"
        context.shop_settings_json = frappe.as_json({
            "shop_name": "Gift Shop",
            "shop_tagline": "",
            "logo": "",
            "primary_colour": "#EE2435",
            "secondary_colour": "#011E41",
            "contact_email": "",
            "contact_phone": "",
            "enable_guest_checkout": True,
        })
