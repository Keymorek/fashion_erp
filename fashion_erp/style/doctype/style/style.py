import frappe
from frappe import _
from frappe.model.document import Document

from fashion_erp.style.services.style_service import (
    GENDER_OPTIONS,
    LAUNCH_STATUS_OPTIONS,
    SALES_STATUS_OPTIONS,
    SEASON_OPTIONS,
    coerce_non_negative_float,
    coerce_non_negative_int,
    ensure_enabled_link,
    ensure_link_exists,
    get_current_year,
    normalize_business_code,
    normalize_select,
    normalize_text,
    sync_style_color_row,
)


class Style(Document):
    def validate(self) -> None:
        self._normalize_fields()
        self._validate_links()
        self._sync_style_colors()
        self._validate_style_colors()

    def _normalize_fields(self) -> None:
        self.style_code = normalize_business_code(self.style_code, "Style Code")
        self.style_name = normalize_text(self.style_name)
        self.category = normalize_text(self.category)
        self.sub_category = normalize_text(self.sub_category)
        self.season = normalize_select(
            self.season, "Season", SEASON_OPTIONS, uppercase=True
        )
        self.year = coerce_non_negative_int(self.year, "Year", get_current_year())
        if self.year < 2000 or self.year > 2100:
            frappe.throw(_("Year must be between 2000 and 2100."))

        self.wave = normalize_text(self.wave)
        self.gender = normalize_select(
            self.gender, "Gender", GENDER_OPTIONS, default="Women"
        )
        self.design_owner = normalize_text(self.design_owner)
        self.fabric_main = normalize_text(self.fabric_main)
        self.fabric_lining = normalize_text(self.fabric_lining)
        self.target_cost = coerce_non_negative_float(self.target_cost, "Target Cost")
        self.tag_price = coerce_non_negative_float(self.tag_price, "Tag Price")
        self.launch_status = normalize_select(
            self.launch_status,
            "Launch Status",
            LAUNCH_STATUS_OPTIONS,
            default="Draft",
        )
        self.sales_status = normalize_select(
            self.sales_status,
            "Sales Status",
            SALES_STATUS_OPTIONS,
            default="Not Ready",
        )
        self.description = normalize_text(self.description)

    def _validate_links(self) -> None:
        ensure_link_exists("Brand", self.brand)
        ensure_link_exists("Item Group", self.item_group)
        ensure_enabled_link("Size System", self.size_system)
        ensure_link_exists("Item", self.item_template)

    def _sync_style_colors(self) -> None:
        if not self.colors:
            frappe.throw(_("At least one Style Color row is required."))

        for index, row in enumerate(self.colors, start=1):
            default_sort_order = index * 10
            sync_style_color_row(row, default_sort_order)

    def _validate_style_colors(self) -> None:
        seen_colors = set()
        enabled_rows = 0

        for row in self.colors:
            if row.color in seen_colors:
                frappe.throw(
                    _("Duplicate Style Color {0} is not allowed.").format(
                        frappe.bold(row.color)
                    )
                )
            seen_colors.add(row.color)

            if row.enabled:
                enabled_rows += 1

        if enabled_rows <= 0:
            frappe.throw(_("At least one enabled Style Color is required."))
