from frappe import _
from frappe.model.document import Document

from fashion_erp.style.services.style_service import (
    ensure_link_exists,
    normalize_select,
    normalize_text,
)


CHANNEL_OPTIONS = ("Manual", "TikTok", "Shopee", "Shopify")
CHANNEL_STORE_STATUS_OPTIONS = ("Draft", "Active", "Disabled")


class ChannelStore(Document):
    def validate(self) -> None:
        self.channel = normalize_select(
            self.channel,
            "Channel",
            CHANNEL_OPTIONS,
            default="Manual",
        )
        self.store_name = normalize_text(self.store_name)
        self.status = normalize_select(
            self.status,
            "Status",
            CHANNEL_STORE_STATUS_OPTIONS,
            default="Draft",
        )
        self.api_config_ref = normalize_text(self.api_config_ref)

        ensure_link_exists("Warehouse", self.warehouse)
        ensure_link_exists("Price List", self.price_list)

        if self.status == "Active" and not self.warehouse:
            from frappe import throw

            throw(_("Warehouse is required when Channel Store status is Active."))
