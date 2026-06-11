app_name = "onerc_giftshop"
app_title = "OneRC Gift Shop"
app_publisher = "Kelvin Njenga"
app_description = "Multi-branch gift shop platform for humanitarian organisations"
app_email = "njengasheba@gmail.com"
app_license = "mit"

required_apps = ["frappe", "erpnext", "onerc_core"]

after_install = "onerc_giftshop.setup.after_install"

fixtures = [
	{"dt": "Role", "filters": [["role_name", "in", [
		"Shop Administrator",
		"Shop Branch Manager",
		"Shop Region Manager",
		"Shop Finance",
	]]]},
	{"dt": "Shop Notification Template", "filters": [["is_active", "=", 1]]},
]

scheduler_events = {
	"daily": [
		"onerc_giftshop.tasks.check_low_stock",
		"onerc_giftshop.tasks.check_remittance_thresholds",
		"onerc_giftshop.tasks.expire_abandoned_carts",
	],
}

website_route_rules = [
	{"from_route": "/shop-manager/<path:subpath>", "to_route": "shop-manager"},
	{"from_route": "/shop/<path:subpath>", "to_route": "shop"},
]
