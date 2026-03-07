import frappe
from frappe import _
from frappe.utils import now_datetime, nowdate

from fashion_erp.style.services.style_service import (
    coerce_non_negative_int,
    ensure_link_exists,
    get_color_metadata,
    normalize_select,
    normalize_text,
)


PRODUCTION_STAGE_OPTIONS = ("Planned", "Cutting", "Stitching", "Finishing", "Packing", "Done")
PRODUCTION_STATUS_OPTIONS = ("Draft", "In Progress", "Hold", "Completed", "Cancelled")
NEXT_STAGE_BY_STAGE = {
    "Planned": "Cutting",
    "Cutting": "Stitching",
    "Stitching": "Finishing",
    "Finishing": "Packing",
    "Packing": "Done",
    "Done": "Done",
}


def validate_production_ticket(doc) -> None:
    doc.stage = normalize_select(
        doc.stage,
        "Stage",
        PRODUCTION_STAGE_OPTIONS,
        default="Planned",
    )
    doc.status = normalize_select(
        doc.status,
        "Status",
        PRODUCTION_STATUS_OPTIONS,
        default="Draft",
    )
    doc.qty = coerce_non_negative_int(doc.qty, "Qty")
    doc.defect_qty = coerce_non_negative_int(doc.defect_qty, "Defect Qty")
    doc.remark = normalize_text(doc.remark)

    ensure_link_exists("Style", doc.style)
    ensure_link_exists("Item", doc.item_template)
    ensure_link_exists("BOM", doc.bom_no)
    ensure_link_exists("Work Order", doc.work_order)
    ensure_link_exists("Supplier", doc.supplier)

    _sync_style_defaults(doc)
    _sync_ticket_color(doc)
    _sync_stage_logs(doc)
    _validate_dates(doc)
    _validate_business_rules(doc)


def start_production_ticket(ticket_name: str) -> dict[str, object]:
    doc = _get_ticket_doc(ticket_name)
    _ensure_ticket_mutable(doc)

    if doc.stage == "Planned":
        doc.stage = "Cutting"

    doc.status = "In Progress"
    doc.actual_start_date = doc.actual_start_date or nowdate()
    doc.save(ignore_permissions=True)

    return _build_ticket_response(doc, _("Production Ticket started."))


def advance_production_ticket_stage(ticket_name: str) -> dict[str, object]:
    doc = _get_ticket_doc(ticket_name)
    _ensure_ticket_mutable(doc)

    next_stage = NEXT_STAGE_BY_STAGE.get(doc.stage or "Planned", "Done")
    if next_stage == doc.stage == "Done":
        frappe.throw(_("Production Ticket is already at the final stage."))

    doc.stage = next_stage
    doc.status = "Completed" if next_stage == "Done" else "In Progress"
    doc.actual_start_date = doc.actual_start_date or nowdate()
    if next_stage == "Done":
        doc.actual_end_date = doc.actual_end_date or nowdate()

    doc.save(ignore_permissions=True)
    return _build_ticket_response(
        doc,
        _("Production Ticket moved to stage {0}.").format(frappe.bold(doc.stage)),
    )


def hold_production_ticket(ticket_name: str) -> dict[str, object]:
    doc = _get_ticket_doc(ticket_name)
    _ensure_ticket_mutable(doc)

    doc.status = "Hold"
    doc.save(ignore_permissions=True)
    return _build_ticket_response(doc, _("Production Ticket is now on hold."))


def resume_production_ticket(ticket_name: str) -> dict[str, object]:
    doc = _get_ticket_doc(ticket_name)
    _ensure_ticket_mutable(doc)

    if doc.stage == "Planned":
        doc.stage = "Cutting"

    doc.status = "In Progress"
    doc.actual_start_date = doc.actual_start_date or nowdate()
    doc.save(ignore_permissions=True)
    return _build_ticket_response(doc, _("Production Ticket resumed."))


def complete_production_ticket(ticket_name: str) -> dict[str, object]:
    doc = _get_ticket_doc(ticket_name)
    _ensure_ticket_mutable(doc)

    doc.stage = "Done"
    doc.status = "Completed"
    doc.actual_start_date = doc.actual_start_date or nowdate()
    doc.actual_end_date = doc.actual_end_date or nowdate()
    doc.save(ignore_permissions=True)

    return _build_ticket_response(doc, _("Production Ticket completed."))


def add_stage_log_to_ticket(
    ticket_name: str,
    *,
    stage: str | None = None,
    qty_in: int | str | None = None,
    qty_out: int | str | None = None,
    defect_qty: int | str | None = None,
    warehouse: str | None = None,
    supplier: str | None = None,
    remark: str | None = None,
) -> dict[str, object]:
    doc = _get_ticket_doc(ticket_name)
    _ensure_ticket_mutable(doc)

    log_stage = normalize_select(
        stage,
        "Stage",
        PRODUCTION_STAGE_OPTIONS,
        default=doc.stage or "Planned",
    )

    doc.append(
        "stage_logs",
        {
            "stage": log_stage,
            "qty_in": coerce_non_negative_int(qty_in, "Qty In"),
            "qty_out": coerce_non_negative_int(qty_out, "Qty Out"),
            "defect_qty": coerce_non_negative_int(defect_qty, "Defect Qty"),
            "warehouse": warehouse,
            "supplier": supplier or doc.supplier,
            "log_time": now_datetime(),
            "remark": normalize_text(remark),
        },
    )

    if log_stage == "Done":
        doc.stage = "Done"
        doc.status = "Completed"
        doc.actual_end_date = doc.actual_end_date or nowdate()
    else:
        doc.stage = log_stage
        doc.status = "In Progress"

    doc.actual_start_date = doc.actual_start_date or nowdate()
    doc.save(ignore_permissions=True)

    return _build_ticket_response(doc, _("Stage Log added to Production Ticket."))


def _get_ticket_doc(ticket_name: str):
    if not ticket_name:
        frappe.throw(_("Production Ticket is required."))
    return frappe.get_doc("Production Ticket", ticket_name)


def _sync_style_defaults(doc) -> None:
    if not doc.style:
        return

    style_item_template = frappe.db.get_value("Style", doc.style, "item_template")
    if style_item_template and not doc.item_template:
        doc.item_template = style_item_template


def _sync_ticket_color(doc) -> None:
    if not doc.color:
        frappe.throw(_("Color is required."))

    color_data = get_color_metadata(doc.color)
    doc.color = color_data["color"]
    doc.color_name = color_data["color_name"]
    doc.color_code = color_data["color_code"]

    if not doc.style:
        return

    allowed_colors = set(
        frappe.get_all(
            "Style Color",
            filters={"parent": doc.style, "parenttype": "Style", "parentfield": "colors"},
            pluck="color",
        )
    )
    if allowed_colors and doc.color not in allowed_colors:
        frappe.throw(
            _("Color {0} is not configured on Style {1}.").format(
                frappe.bold(doc.color), frappe.bold(doc.style)
            )
        )


def _sync_stage_logs(doc) -> None:
    if not doc.stage_logs:
        return

    total_defect_qty = 0
    for row in doc.stage_logs:
        row.stage = normalize_select(
            row.stage,
            "Stage Log Stage",
            PRODUCTION_STAGE_OPTIONS,
            default=doc.stage or "Planned",
        )
        row.qty_in = coerce_non_negative_int(row.qty_in, "Qty In")
        row.qty_out = coerce_non_negative_int(row.qty_out, "Qty Out")
        row.defect_qty = coerce_non_negative_int(row.defect_qty, "Defect Qty")
        row.remark = normalize_text(row.remark)
        row.log_time = row.log_time or now_datetime()

        if row.qty_in and row.qty_out + row.defect_qty > row.qty_in:
            frappe.throw(
                _("Stage Log output plus defect quantity cannot exceed Qty In for stage {0}.").format(
                    frappe.bold(row.stage)
                )
            )

        ensure_link_exists("Warehouse", row.warehouse)
        ensure_link_exists("Supplier", row.supplier)
        total_defect_qty += row.defect_qty

    doc.defect_qty = total_defect_qty


def _validate_dates(doc) -> None:
    if doc.planned_start_date and doc.planned_end_date and doc.planned_end_date < doc.planned_start_date:
        frappe.throw(_("Planned End Date cannot be earlier than Planned Start Date."))

    if doc.actual_start_date and doc.actual_end_date and doc.actual_end_date < doc.actual_start_date:
        frappe.throw(_("Actual End Date cannot be earlier than Actual Start Date."))


def _validate_business_rules(doc) -> None:
    if doc.status == "Completed":
        doc.stage = "Done"
        doc.actual_end_date = doc.actual_end_date or nowdate()
        doc.actual_start_date = doc.actual_start_date or doc.actual_end_date

    if doc.status == "In Progress":
        doc.actual_start_date = doc.actual_start_date or nowdate()

    if doc.stage == "Done" and doc.status == "Draft":
        frappe.throw(_("Status cannot remain Draft when Stage is Done."))


def _ensure_ticket_mutable(doc) -> None:
    if doc.status == "Cancelled":
        frappe.throw(_("Cancelled Production Ticket cannot be modified."))
    if doc.status == "Completed":
        frappe.throw(_("Completed Production Ticket cannot be modified."))


def _build_ticket_response(doc, message: str) -> dict[str, object]:
    return {
        "ok": True,
        "name": doc.name,
        "style": doc.style,
        "color": doc.color,
        "color_code": doc.color_code,
        "stage": doc.stage,
        "status": doc.status,
        "qty": doc.qty,
        "defect_qty": doc.defect_qty,
        "actual_start_date": doc.actual_start_date,
        "actual_end_date": doc.actual_end_date,
        "message": message,
    }
