app_name = "hallbooking"
app_title = "Hallbooking"
app_publisher = "Pankaj Sharma"
app_description = "Conference Hall Booking"
app_email = "pankaj.sharma@vcm.org.in"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "hallbooking",
# 		"logo": "/assets/hallbooking/logo.png",
# 		"title": "Hallbooking",
# 		"route": "/hallbooking",
# 		"has_permission": "hallbooking.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hallbooking/css/hallbooking.css"
# app_include_js = "/assets/hallbooking/js/hallbooking.js"

# include js, css files in header of web template
# web_include_css = "/assets/hallbooking/css/hallbooking.css"
# web_include_js = "/assets/hallbooking/js/hallbooking.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hallbooking/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hallbooking/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hallbooking.utils.jinja_methods",
# 	"filters": "hallbooking.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hallbooking.install.before_install"
# after_install = "hallbooking.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hallbooking.uninstall.before_uninstall"
# after_uninstall = "hallbooking.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hallbooking.utils.before_app_install"
# after_app_install = "hallbooking.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hallbooking.utils.before_app_uninstall"
# after_app_uninstall = "hallbooking.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hallbooking.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hallbooking.tasks.all"
# 	],
# 	"daily": [
# 		"hallbooking.tasks.daily"
# 	],
# 	"hourly": [
# 		"hallbooking.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hallbooking.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hallbooking.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hallbooking.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hallbooking.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hallbooking.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hallbooking.utils.before_request"]
# after_request = ["hallbooking.utils.after_request"]

# Job Events
# ----------
# before_job = ["hallbooking.utils.before_job"]
# after_job = ["hallbooking.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hallbooking.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }


# api_paths = [
#     {"method": "POST", "path": "approve_booking", "handler": "hallbooking.hallbooking_custom.api.booking.approve_booking"},
#     {"method": "POST", "path": "cancel_booking", "handler": "hallbooking.hallbooking_custom.api.booking.cancel_booking"}
# ]

api_paths = [
    {"method": "PUT", "path": "update_booking_status", "handler": "hallbooking.hallbooking_custom.api.booking.update_booking_status"}
]
# api_paths = [
#     {"method": "PUT", "path": "/api/method/hallbooking_custom.api.booking.update_booking_status"}
# ]

# doc_events = {
#     "booking": {
#         "on_update": "hallbooking.api.update_booking_status"
#     }
# }
