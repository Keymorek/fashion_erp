import re

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate


BUSINESS_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]*$")
SEASON_OPTIONS = ("SS", "AW", "ALL")
GENDER_OPTIONS = ("Women", "Unisex", "Kids")
LAUNCH_STATUS_OPTIONS = ("Draft", "Sampling", "Approved", "Ready", "Launched", "Archived")
SALES_STATUS_OPTIONS = ("Not Ready", "On Sale", "Stop Sale", "Clearance", "Discontinued")

COLOR_GROUP_SEEDS = [
    {"color_group_code": "WHT", "color_group_name": "白色系", "sort_order": 10, "enabled": 1},
    {"color_group_code": "BLK", "color_group_name": "黑色系", "sort_order": 20, "enabled": 1},
    {"color_group_code": "GRY", "color_group_name": "灰色系", "sort_order": 30, "enabled": 1},
    {"color_group_code": "BLU", "color_group_name": "蓝色系", "sort_order": 40, "enabled": 1},
    {"color_group_code": "RED", "color_group_name": "红色系", "sort_order": 50, "enabled": 1},
    {"color_group_code": "PNK", "color_group_name": "粉色系", "sort_order": 60, "enabled": 1},
    {"color_group_code": "GRN", "color_group_name": "绿色系", "sort_order": 70, "enabled": 1},
    {"color_group_code": "BRN", "color_group_name": "棕色系", "sort_order": 80, "enabled": 1},
    {"color_group_code": "KHK", "color_group_name": "卡其色系", "sort_order": 90, "enabled": 1},
    {"color_group_code": "YLW", "color_group_name": "黄色系", "sort_order": 100, "enabled": 1},
]

COLOR_SEEDS = [
    {"color_name": "奶油白", "color_group": "WHT", "enabled": 1},
    {"color_name": "米白", "color_group": "WHT", "enabled": 1},
    {"color_name": "象牙白", "color_group": "WHT", "enabled": 1},
    {"color_name": "本白", "color_group": "WHT", "enabled": 1},
    {"color_name": "冷白", "color_group": "WHT", "enabled": 1},
    {"color_name": "黑色", "color_group": "BLK", "enabled": 1},
    {"color_name": "炭灰", "color_group": "GRY", "enabled": 1},
    {"color_name": "藏蓝", "color_group": "BLU", "enabled": 1},
    {"color_name": "酒红", "color_group": "RED", "enabled": 1},
    {"color_name": "豆沙粉", "color_group": "PNK", "enabled": 1},
    {"color_name": "军绿", "color_group": "GRN", "enabled": 1},
    {"color_name": "巧克力棕", "color_group": "BRN", "enabled": 1},
    {"color_name": "卡其", "color_group": "KHK", "enabled": 1},
    {"color_name": "奶黄", "color_group": "YLW", "enabled": 1},
]

SIZE_SYSTEM_SEEDS = [
    {
        "size_system_code": "TOP",
        "size_system_name": "上装尺码",
        "applicable_products": "T恤、衬衫、针织衫、卫衣、外套",
        "enabled": 1,
    },
    {
        "size_system_code": "DRESS",
        "size_system_name": "连衣裙尺码",
        "applicable_products": "连衣裙",
        "enabled": 1,
    },
    {
        "size_system_code": "BOTTOM",
        "size_system_name": "裤装尺码",
        "applicable_products": "牛仔裤、休闲裤",
        "enabled": 1,
    },
    {
        "size_system_code": "SKIRT",
        "size_system_name": "半裙尺码",
        "applicable_products": "短裙、长裙",
        "enabled": 1,
    },
    {
        "size_system_code": "SHOE",
        "size_system_name": "鞋类尺码",
        "applicable_products": "女鞋",
        "enabled": 1,
    },
    {
        "size_system_code": "FREE",
        "size_system_name": "均码体系",
        "applicable_products": "均码商品",
        "enabled": 1,
    },
    {
        "size_system_code": "BRA",
        "size_system_name": "内衣尺码",
        "applicable_products": "内衣",
        "enabled": 1,
    },
    {
        "size_system_code": "ACC",
        "size_system_name": "配饰尺码",
        "applicable_products": "帽子、围巾、腰带等",
        "enabled": 1,
    },
]

SIZE_CODE_SEEDS = [
    {"size_system": "TOP", "size_code": "XXS", "size_name": "XXS", "sort_order": 10, "enabled": 1},
    {"size_system": "TOP", "size_code": "XS", "size_name": "XS", "sort_order": 20, "enabled": 1},
    {"size_system": "TOP", "size_code": "S", "size_name": "S", "sort_order": 30, "enabled": 1},
    {"size_system": "TOP", "size_code": "M", "size_name": "M", "sort_order": 40, "enabled": 1},
    {"size_system": "TOP", "size_code": "L", "size_name": "L", "sort_order": 50, "enabled": 1},
    {"size_system": "TOP", "size_code": "XL", "size_name": "XL", "sort_order": 60, "enabled": 1},
    {"size_system": "TOP", "size_code": "XXL", "size_name": "2XL", "sort_order": 70, "enabled": 1},
    {"size_system": "TOP", "size_code": "XXXL", "size_name": "3XL", "sort_order": 80, "enabled": 1},
    {"size_system": "TOP", "size_code": "F", "size_name": "F", "sort_order": 90, "enabled": 1},
    {"size_system": "DRESS", "size_code": "XS", "size_name": "XS", "sort_order": 10, "enabled": 1},
    {"size_system": "DRESS", "size_code": "S", "size_name": "S", "sort_order": 20, "enabled": 1},
    {"size_system": "DRESS", "size_code": "M", "size_name": "M", "sort_order": 30, "enabled": 1},
    {"size_system": "DRESS", "size_code": "L", "size_name": "L", "sort_order": 40, "enabled": 1},
    {"size_system": "DRESS", "size_code": "XL", "size_name": "XL", "sort_order": 50, "enabled": 1},
    {"size_system": "SKIRT", "size_code": "XS", "size_name": "XS", "sort_order": 10, "enabled": 1},
    {"size_system": "SKIRT", "size_code": "S", "size_name": "S", "sort_order": 20, "enabled": 1},
    {"size_system": "SKIRT", "size_code": "M", "size_name": "M", "sort_order": 30, "enabled": 1},
    {"size_system": "SKIRT", "size_code": "L", "size_name": "L", "sort_order": 40, "enabled": 1},
    {"size_system": "SKIRT", "size_code": "XL", "size_name": "XL", "sort_order": 50, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "24", "size_name": "24", "sort_order": 10, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "25", "size_name": "25", "sort_order": 20, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "26", "size_name": "26", "sort_order": 30, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "27", "size_name": "27", "sort_order": 40, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "28", "size_name": "28", "sort_order": 50, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "29", "size_name": "29", "sort_order": 60, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "30", "size_name": "30", "sort_order": 70, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "31", "size_name": "31", "sort_order": 80, "enabled": 1},
    {"size_system": "BOTTOM", "size_code": "32", "size_name": "32", "sort_order": 90, "enabled": 1},
    {"size_system": "FREE", "size_code": "ONE", "size_name": "One Size", "sort_order": 10, "enabled": 1},
    {"size_system": "ACC", "size_code": "ONE", "size_name": "One Size", "sort_order": 10, "enabled": 1},
]


def normalize_text(value: str | None) -> str:
    return (value or "").strip()


def normalize_business_code(value: str | None, field_label: str) -> str:
    code = normalize_text(value).upper()
    if code and not BUSINESS_CODE_PATTERN.fullmatch(code):
        frappe.throw(
            _("{0} must contain only uppercase letters, numbers, hyphen, or underscore.").format(
                field_label
            )
        )
    return code


def coerce_checkbox(value: object, default: int = 1) -> int:
    if value in (None, ""):
        return default
    return 1 if cint(value) else 0


def coerce_non_negative_int(value: object, field_label: str, default: int = 0) -> int:
    number = cint(value if value not in (None, "") else default)
    if number < 0:
        frappe.throw(_("{0} cannot be negative.").format(field_label))
    return number


def coerce_non_negative_float(value: object, field_label: str, default: float = 0) -> float:
    number = flt(value if value not in (None, "") else default)
    if number < 0:
        frappe.throw(_("{0} cannot be negative.").format(field_label))
    return number


def normalize_select(
    value: str | None,
    field_label: str,
    allowed_values: tuple[str, ...],
    *,
    default: str | None = None,
    uppercase: bool = False,
) -> str:
    normalized = normalize_text(value) or normalize_text(default)
    if uppercase:
        normalized = normalized.upper()
    if normalized and normalized not in allowed_values:
        frappe.throw(
            _("{0} must be one of: {1}.").format(field_label, ", ".join(allowed_values))
        )
    return normalized


def ensure_link_exists(doctype: str, name: str | None) -> None:
    if not name:
        return
    if not frappe.db.exists(doctype, name):
        frappe.throw(_("{0} {1} does not exist.").format(doctype, frappe.bold(name)))


def is_enabled_doc(doctype: str, name: str | None, enabled_field: str = "enabled") -> bool:
    if not name or not frappe.db.exists(doctype, name):
        return False
    value = frappe.db.get_value(doctype, name, enabled_field)
    if value is None:
        return True
    return bool(cint(value))


def ensure_enabled_link(doctype: str, name: str | None, enabled_field: str = "enabled") -> None:
    ensure_link_exists(doctype, name)
    if name and not is_enabled_doc(doctype, name, enabled_field):
        frappe.throw(_("{0} {1} is disabled.").format(doctype, frappe.bold(name)))


def get_current_year() -> int:
    return int(nowdate().split("-")[0])


def has_brand_abbreviation_field() -> bool:
    return frappe.get_meta("Brand").has_field("brand_abbr")


def get_brand_abbreviation(brand_name: str | None, *, raise_on_missing_meta: bool = False) -> str:
    if not brand_name:
        return ""

    ensure_link_exists("Brand", brand_name)

    if not has_brand_abbreviation_field():
        if raise_on_missing_meta:
            frappe.throw(_("Brand Abbr field is missing on Brand. Apply Fashion ERP fixtures first."))
        return ""

    brand_abbr = frappe.db.get_value("Brand", brand_name, "brand_abbr")
    return normalize_business_code(brand_abbr, "Brand Abbr")


def get_color_metadata(color_name: str | None) -> dict[str, object]:
    if not color_name:
        frappe.throw(_("Color is required."))

    color = frappe.db.get_value(
        "Color",
        color_name,
        ["name", "color_name", "color_group", "enabled"],
        as_dict=True,
    )
    if not color:
        frappe.throw(_("Color {0} does not exist.").format(frappe.bold(color_name)))
    if not cint(color.enabled):
        frappe.throw(_("Color {0} is disabled.").format(frappe.bold(color_name)))

    group = frappe.db.get_value(
        "Color Group",
        color.color_group,
        ["name", "color_group_code", "enabled"],
        as_dict=True,
    )
    if not group:
        frappe.throw(
            _("Color Group {0} does not exist for Color {1}.").format(
                frappe.bold(color.color_group), frappe.bold(color_name)
            )
        )
    if not cint(group.enabled):
        frappe.throw(_("Color Group {0} is disabled.").format(frappe.bold(group.name)))

    return {
        "color": color.name,
        "color_name": color.color_name,
        "color_group": color.color_group,
        "color_code": group.color_group_code,
    }


def sync_style_color_row(row, default_sort_order: int = 0) -> None:
    color_data = get_color_metadata(row.color)
    row.color = color_data["color"]
    row.color_name = color_data["color_name"]
    row.color_code = color_data["color_code"]
    row.sort_order = coerce_non_negative_int(row.sort_order, "Style Color Sort Order", default_sort_order)
    row.enabled = coerce_checkbox(row.enabled)


def get_enabled_size_codes(size_system: str | None) -> list[str]:
    if not size_system:
        return []
    return frappe.get_all(
        "Size Code",
        filters={"size_system": size_system, "enabled": 1},
        pluck="size_code",
        order_by="sort_order asc, size_code asc",
    )


def get_style_variant_generation_issues(style_doc) -> list[str]:
    issues = []

    if not style_doc.brand:
        issues.append(_("Brand is required before generating SKU Items."))
    else:
        if not has_brand_abbreviation_field():
            issues.append(_("Brand Abbr field is missing on Brand. Apply Fashion ERP fixtures first."))
        elif not get_brand_abbreviation(style_doc.brand):
            issues.append(
                _("Brand Abbr is required on Brand {0} before generating SKU Items.").format(
                    frappe.bold(style_doc.brand)
                )
            )

    if not style_doc.size_system:
        issues.append(_("Size System is required."))
    elif not is_enabled_doc("Size System", style_doc.size_system):
        issues.append(_("Size System {0} is disabled.").format(frappe.bold(style_doc.size_system)))
    elif not get_enabled_size_codes(style_doc.size_system):
        issues.append(
            _("Size System {0} has no enabled Size Codes.").format(
                frappe.bold(style_doc.size_system)
            )
        )

    if not style_doc.item_group:
        issues.append(_("Item Group is required before generating SKU Items."))

    enabled_colors = [row for row in (style_doc.colors or []) if cint(row.enabled)]
    if not enabled_colors:
        issues.append(_("At least one enabled Style Color is required."))

    return issues


def seed_master_data() -> None:
    for row in COLOR_GROUP_SEEDS:
        _upsert_named_doc("Color Group", "color_group_code", row)

    for row in COLOR_SEEDS:
        ensure_link_exists("Color Group", row["color_group"])
        _upsert_named_doc("Color", "color_name", row)

    for row in SIZE_SYSTEM_SEEDS:
        _upsert_named_doc("Size System", "size_system_code", row)

    for row in SIZE_CODE_SEEDS:
        ensure_link_exists("Size System", row["size_system"])
        _upsert_size_code(row)


def _upsert_named_doc(doctype: str, name_field: str, values: dict[str, object]) -> str:
    docname = values[name_field]
    if frappe.db.exists(doctype, docname):
        doc = frappe.get_doc(doctype, docname)
        changed = False
        for fieldname, value in values.items():
            if doc.get(fieldname) != value:
                doc.set(fieldname, value)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
        return doc.name

    doc = frappe.get_doc({"doctype": doctype, **values})
    doc.insert(ignore_permissions=True)
    return doc.name


def _upsert_size_code(values: dict[str, object]) -> str:
    filters = {"size_system": values["size_system"], "size_code": values["size_code"]}
    existing = frappe.db.get_value("Size Code", filters, "name")
    if existing:
        doc = frappe.get_doc("Size Code", existing)
        changed = False
        for fieldname, value in values.items():
            if doc.get(fieldname) != value:
                doc.set(fieldname, value)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
        return doc.name

    doc = frappe.get_doc({"doctype": "Size Code", **values})
    doc.insert(ignore_permissions=True)
    return doc.name
