import frappe
from frappe import _

from fashion_erp.stock.services.sales_order_fulfillment_service import (
    sync_linked_sales_orders_fulfillment_status as _sync_linked_sales_orders_fulfillment_status,
    sync_sales_order_fulfillment_status,
)
from fashion_erp.style.services.style_service import ensure_link_exists, normalize_text


def validate_sales_order_channel_context(doc, method=None) -> None:
    doc.channel_store = normalize_text(getattr(doc, "channel_store", None))
    doc.channel = normalize_text(getattr(doc, "channel", None))
    doc.external_order_id = normalize_text(getattr(doc, "external_order_id", None))
    doc.after_sales_ticket = normalize_text(getattr(doc, "after_sales_ticket", None))

    if doc.channel_store:
        ensure_link_exists("Channel Store", doc.channel_store)
        store_channel = normalize_text(frappe.db.get_value("Channel Store", doc.channel_store, "channel"))
        if store_channel and doc.channel and doc.channel != store_channel:
            frappe.throw(_("渠道店铺对应渠道为 {0}，不能手工填写为 {1}。").format(
                frappe.bold(store_channel),
                frappe.bold(doc.channel),
            ))
        if store_channel:
            doc.channel = store_channel

    if doc.external_order_id and not doc.channel_store:
        frappe.throw(_("填写外部订单号时必须先填写渠道店铺。"))

    _validate_external_order_uniqueness(doc)
    sync_sales_order_fulfillment_status(doc)


def sync_after_sales_replacement_order(doc, method=None) -> None:
    after_sales_ticket = normalize_text(getattr(doc, "after_sales_ticket", None))
    if not after_sales_ticket:
        return

    ticket_row = frappe.db.get_value(
        "After Sales Ticket",
        after_sales_ticket,
        ["replacement_sales_order"],
        as_dict=True,
    ) or {}
    if not ticket_row:
        return

    current_value = normalize_text(ticket_row.get("replacement_sales_order"))
    if current_value == normalize_text(getattr(doc, "name", None)):
        return

    ticket = frappe.get_doc("After Sales Ticket", after_sales_ticket)
    ticket.db_set("replacement_sales_order", doc.name, update_modified=False)


def sync_linked_sales_orders_fulfillment_status(doc, method=None) -> None:
    _sync_linked_sales_orders_fulfillment_status(doc)


def _validate_external_order_uniqueness(doc) -> None:
    if not doc.channel_store or not doc.external_order_id:
        return
    if doc.after_sales_ticket:
        return

    rows = frappe.get_all(
        "Sales Order",
        filters=[
            ["Sales Order", "channel_store", "=", doc.channel_store],
            ["Sales Order", "external_order_id", "=", doc.external_order_id],
            ["Sales Order", "docstatus", "<", 2],
        ],
        fields=["name", "after_sales_ticket"],
    )
    for row in rows or []:
        name = normalize_text(row.get("name"))
        if not name or name == normalize_text(getattr(doc, "name", None)):
            continue
        if normalize_text(row.get("after_sales_ticket")):
            continue
        frappe.throw(
            _("渠道店铺 {0} 下的外部订单号 {1} 已存在于销售订单 {2}。").format(
                frappe.bold(doc.channel_store),
                frappe.bold(doc.external_order_id),
                frappe.bold(name),
            )
        )
