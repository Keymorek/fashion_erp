import frappe
from frappe import _
from frappe.model.document import Document

from fashion_erp.style.services.style_service import (
    coerce_checkbox,
    coerce_non_negative_int,
    ensure_link_exists,
    normalize_business_code,
    normalize_text,
)


class SizeCode(Document):
    def validate(self) -> None:
        self.size_system = normalize_business_code(self.size_system, "Size System")
        self.size_code = normalize_business_code(self.size_code, "Size Code")
        self.size_name = normalize_text(self.size_name) or self.size_code
        self.sort_order = coerce_non_negative_int(self.sort_order, "Sort Order")
        self.enabled = coerce_checkbox(self.enabled)

        ensure_link_exists("Size System", self.size_system)
        self._validate_unique_size_code()

    def _validate_unique_size_code(self) -> None:
        filters = {"size_system": self.size_system, "size_code": self.size_code}
        existing = frappe.db.get_value("Size Code", filters, "name")
        if existing and existing != self.name:
            frappe.throw(
                _("Size Code {0} already exists under Size System {1}.").format(
                    frappe.bold(self.size_code), frappe.bold(self.size_system)
                )
            )
