app_name = "fashion_erp"
app_title = "Fashion ERP"
app_publisher = "Keymorek"
app_description = "Industry extensions for women's apparel ecommerce and garment manufacturing."
app_email = ""
app_license = "Proprietary"
required_apps = ["erpnext"]
fixtures = ["Custom Field", "Client Script"]

after_install = "fashion_erp.install.after_install"
