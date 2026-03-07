import frappe
from frappe import _

from fashion_erp.style.services.sku_service import (
    build_style_matrix,
    create_template_item_for_style,
    generate_variants_for_style,
)
from fashion_erp.style.services.style_service import get_style_variant_generation_issues


def _get_style(style_name: str):
    if not style_name:
        frappe.throw(_("Style is required."))
    return frappe.get_doc("Style", style_name)


@frappe.whitelist()
def create_template_item(style_name: str) -> dict[str, object]:
    style = _get_style(style_name)
    if style.item_template:
        result = create_template_item_for_style(style_name)
        return {
            "ok": True,
            "message": _("Template Item is linked: {0}.").format(frappe.bold(result["item_code"])),
            "result": result,
        }

    result = create_template_item_for_style(style_name)
    return {
        "ok": True,
        "message": _("Template Item prepared: {0}.").format(frappe.bold(result["item_code"])),
        "result": result,
    }


@frappe.whitelist()
def generate_variants(style_name: str) -> dict[str, object]:
    style = _get_style(style_name)
    issues = get_style_variant_generation_issues(style)
    if issues:
        return {
            "ok": False,
            "message": _("Style is not ready for SKU generation."),
            "issues": issues,
        }

    result = generate_variants_for_style(style_name)
    return {
        "ok": True,
        "message": _(
            "SKU generation completed. Created: {0}, Updated: {1}, Unchanged: {2}."
        ).format(
            len(result["created"]),
            len(result["updated"]),
            len(result["skipped"]),
        ),
        "result": result,
    }


@frappe.whitelist()
def get_style_matrix(style_name: str) -> dict[str, object]:
    style = _get_style(style_name)
    if not style.colors:
        return {
            "ok": False,
            "message": _("Style has no colors yet."),
            "issues": [_("Add at least one Style Color row first.")],
        }

    return {
        "ok": True,
        "result": build_style_matrix(style_name),
    }
